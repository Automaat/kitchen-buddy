#!/usr/bin/env python3
"""Import recipes from Obsidian vault into kitchen-buddy database."""

import re
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.recipe import Recipe, RecipeIngredient
from app.models.ingredient import Ingredient
from app.core.enums import DifficultyLevel


def parse_obsidian_recipe(file_path: Path) -> dict:
    """Parse Obsidian markdown recipe file."""
    content = file_path.read_text(encoding="utf-8")

    # Remove frontmatter if present
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # Extract title from H1 or filename
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem
    has_title_header = bool(title_match)

    # Extract ingredients section
    ingredients = []
    # Try with header first
    ingredients_match = re.search(
        r'##\s+ingredients\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    if ingredients_match:
        ingredients_text = ingredients_match.group(1)
        # Extract list items, remove wiki-links [[...]]
        ingredient_lines = re.findall(r'^[-*]\s+(.+)$', ingredients_text, re.MULTILINE)
        if ingredient_lines:
            ingredients = [re.sub(r'\[\[(.+?)\]\]', r'\1', line.strip()) for line in ingredient_lines]
        else:
            # Fallback: try plain text lines (non-empty lines that aren't headers)
            lines = [l.strip() for l in ingredients_text.split('\n')
                    if l.strip() and not l.strip().startswith('#')]
            if lines:
                ingredients = [re.sub(r'\[\[(.+?)\]\]', r'\1', line) for line in lines]
    else:
        # Try to extract all bullet points after title (if no ingredients header)
        # Look for list items before any other header or end of file
        if has_title_header:
            after_title = re.search(r'^#\s+.+?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            text = after_title.group(1) if after_title else ""
        else:
            # No title header, extract from beginning of content
            text = content

        if text:
            ingredient_lines = re.findall(r'^[-*]\s+(.+)$', text, re.MULTILINE)
            # Only consider it ingredients if we have some lines
            if ingredient_lines:
                ingredients = [re.sub(r'\[\[(.+?)\]\]', r'\1', line.strip()) for line in ingredient_lines]
            else:
                # Last fallback: try plain text lines after title
                lines = [l.strip() for l in text.split('\n')
                        if l.strip() and not l.strip().startswith('#')]
                # Heuristic: extract lines that look like ingredients (short, contain quantities)
                ingredient_pattern = r'^[\d/]+\s*(?:[\d/]+)?\s*(?:to\s+[\d/]+\s+)?(?:cups?|tablespoons?|teaspoons?|g|grams?|ml|oz|lbs?|kg|mg|pinch|dash|stick|package)?'
                ingredient_candidates = []
                for line in lines:
                    # Match if: starts with quantity, or short line with quantity anywhere, or in file with no header
                    has_quantity = bool(re.search(r'\d+\s*(?:ml|g|cup|tsp|tbsp|oz|lb|kg|mg)', line, re.IGNORECASE))
                    if len(line) < 200 and (re.match(ingredient_pattern, line, re.IGNORECASE) or
                                            re.match(r'^[\d.]+\s*[a-z]*\s+\w+', line) or
                                            (not has_title_header and (has_quantity or len(line) < 100))):
                        ingredient_candidates.append(line)
                    elif len(ingredient_candidates) > 0 and len(line) > 100:
                        # Long line after ingredients likely means instructions started
                        break
                if ingredient_candidates and 1 <= len(ingredient_candidates) <= 25:
                    ingredients = [re.sub(r'\[\[(.+?)\]\]', r'\1', line) for line in ingredient_candidates]

    # Extract steps section
    steps = []
    steps_match = re.search(
        r'##\s+(steps?|instructions?)\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    if steps_match:
        steps_text = steps_match.group(2)
        # Extract numbered steps
        step_lines = re.findall(r'^\d+\.\s+(.+)$', steps_text, re.MULTILINE)
        if step_lines:
            steps = [step.strip() for step in step_lines]
        else:
            # Fallback: extract paragraphs as steps if no numbered list found
            paragraphs = [p.strip() for p in steps_text.split('\n\n') if p.strip()]
            if paragraphs:
                steps = paragraphs
    else:
        # Try to extract remaining content after ingredients as instructions
        # This handles recipes with no headers at all
        if not ingredients_match:
            # No headers at all - try to split content after title
            after_title = re.search(r'^#\s+.+?\n(.+)', content, re.DOTALL)
            if after_title:
                remaining_text = after_title.group(1).strip()
                # Skip the first few lines (likely ingredients) and get the rest
                lines = remaining_text.split('\n')
                # Find where ingredient-like lines end (heuristic: lines get longer)
                split_point = 0
                for i, line in enumerate(lines):
                    if i > len(ingredients) and len(line.strip()) > 100:
                        split_point = i
                        break
                if split_point > 0:
                    instruction_lines = lines[split_point:]
                    instruction_text = '\n'.join(instruction_lines).strip()
                    paragraphs = [p.strip() for p in instruction_text.split('\n\n') if p.strip()]
                    if paragraphs:
                        steps = paragraphs

    # Get category from directory structure
    category = file_path.parent.name if file_path.parent.name != "recipes 2" else "other"

    return {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "category": category,
        "file_path": str(file_path)
    }


def parse_ingredient_text(text: str) -> dict:
    """Parse ingredient text to extract quantity, unit, and name."""
    # Pattern: optional quantity + optional unit + ingredient name
    # Examples: "200g flour", "2 cups milk", "salt", "1 large egg"
    pattern = r'^(\d+\.?\d*)\s*([a-zA-Z]*)\s+(.+)$'
    match = re.match(pattern, text)

    if match:
        quantity = match.group(1)
        unit = match.group(2) if match.group(2) else None
        name = match.group(3).strip()
    else:
        # No quantity/unit found, entire text is ingredient name
        quantity = None
        unit = None
        name = text.strip()

    return {
        "quantity": quantity,
        "unit": unit,
        "name": name
    }


def get_or_create_ingredient(db, name: str) -> Ingredient:
    """Get existing ingredient or create new one."""
    # Normalize name: remove leading quantities, units, and other noise
    normalized_name = name.lower().strip()

    # Strip leading quantity patterns (e.g., "1\2 łyżki", "5-6 łyżek", etc.)
    normalized_name = re.sub(r'^[\d\\/\\\-]+\s+', '', normalized_name)  # Remove leading numbers/slashes
    normalized_name = re.sub(r'^(łyżk[ia]|łyżek|ząbk(ów|a|i)|cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|tsp|tbsp|g|ml|oz|kg|pinch|dash|stick)\s+', '', normalized_name, flags=re.IGNORECASE)
    normalized_name = normalized_name.strip()

    # Try to find existing (use exact match since we normalized)
    ingredient = db.query(Ingredient).filter(
        Ingredient.name.ilike(normalized_name)
    ).first()

    if not ingredient:
        ingredient = Ingredient(name=normalized_name)
        db.add(ingredient)
        db.flush()

    return ingredient


def import_recipe(db, parsed_recipe: dict, dry_run: bool = False, update: bool = False) -> tuple[Recipe | None, str]:
    """Import a single recipe into database.

    Returns tuple of (Recipe, status) where status is 'imported', 'skipped', 'updated', or 'error'
    """
    # Check if recipe already exists
    existing = db.query(Recipe).filter(
        Recipe.title == parsed_recipe["title"]
    ).first()

    if existing:
        if not update:
            print(f"  ⚠️  Recipe '{parsed_recipe['title']}' already exists (ID: {existing.id})")
            return existing, "skipped"

        # Update existing recipe
        instructions = "\n".join(f"{i+1}. {step}" for i, step in enumerate(parsed_recipe["steps"]))
        existing.instructions = instructions if instructions else existing.instructions

        if not dry_run:
            # Delete existing ingredients
            db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == existing.id).delete()

            # Add new ingredients
            for ing_text in parsed_recipe["ingredients"]:
                parsed_ing = parse_ingredient_text(ing_text)
                ingredient = get_or_create_ingredient(db, parsed_ing["name"])

                recipe_ing = RecipeIngredient(
                    recipe_id=existing.id,
                    ingredient_id=ingredient.id,
                    quantity=parsed_ing["quantity"],
                    unit=parsed_ing["unit"]
                )
                db.add(recipe_ing)

            db.commit()
            print(f"  🔄 Updated '{existing.title}' (ID: {existing.id}, {len(parsed_recipe['ingredients'])} ingredients)")
            return existing, "updated"
        else:
            print(f"  [DRY RUN] Would update '{existing.title}' with {len(parsed_recipe['ingredients'])} ingredients")
            return existing, "updated"

    # Build instructions from steps
    instructions = "\n".join(f"{i+1}. {step}" for i, step in enumerate(parsed_recipe["steps"]))

    # Create recipe
    recipe = Recipe(
        title=parsed_recipe["title"],
        instructions=instructions if instructions else None,
        difficulty=DifficultyLevel.MEDIUM,  # Default
        servings=4,  # Default
    )

    if not dry_run:
        db.add(recipe)
        db.flush()  # Get recipe ID

        # Add ingredients
        for ing_text in parsed_recipe["ingredients"]:
            parsed_ing = parse_ingredient_text(ing_text)
            ingredient = get_or_create_ingredient(db, parsed_ing["name"])

            recipe_ing = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=parsed_ing["quantity"],
                unit=parsed_ing["unit"]
            )
            db.add(recipe_ing)

        db.commit()
        print(f"  ✅ Imported '{recipe.title}' (ID: {recipe.id}, {len(parsed_recipe['ingredients'])} ingredients)")
        return recipe, "imported"
    else:
        print(f"  [DRY RUN] Would import '{recipe.title}' with {len(parsed_recipe['ingredients'])} ingredients")
        return None, "imported"


def main():
    """Main import function."""
    obsidian_recipes_path = Path(
        "/Users/marcin.skalski@konghq.com/Library/Mobile Documents/"
        "iCloud~md~obsidian/Documents/second-brain/3_Resources/Cooking/recipes 2"
    )

    # Find all recipe markdown files
    recipe_files = list(obsidian_recipes_path.rglob("*.md"))
    print(f"Found {len(recipe_files)} recipe files in Obsidian vault\n")

    # Parse all recipes
    parsed_recipes = []
    for file_path in sorted(recipe_files):
        try:
            parsed = parse_obsidian_recipe(file_path)
            parsed_recipes.append(parsed)
        except Exception as e:
            print(f"❌ Error parsing {file_path.name}: {e}")

    print(f"\nSuccessfully parsed {len(parsed_recipes)} recipes")
    print("\nImporting to database...\n")

    # Import to database
    db = SessionLocal()
    try:
        dry_run = "--dry-run" in sys.argv
        update = "--update" in sys.argv
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made\n")
        if update:
            print("🔄 UPDATE MODE - Existing recipes will be updated\n")

        imported_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for parsed_recipe in parsed_recipes:
            try:
                recipe, status = import_recipe(db, parsed_recipe, dry_run=dry_run, update=update)
                if status == "imported":
                    imported_count += 1
                elif status == "updated":
                    updated_count += 1
                elif status == "skipped":
                    skipped_count += 1
            except Exception as e:
                print(f"❌ Error importing '{parsed_recipe['title']}': {e}")
                error_count += 1
                db.rollback()

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
        print(f"  Imported: {imported_count}")
        if update:
            print(f"  Updated: {updated_count}")
        print(f"  Skipped (already exist): {skipped_count}")
        if error_count:
            print(f"  Errors: {error_count}")
        print(f"  Total: {len(parsed_recipes)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
