from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core import get_db
from app.models import PantryItem, Recipe
from app.schemas import RecipeSuggestion, SuggestionsResponse, MissingIngredient

router = APIRouter()


@router.get("", response_model=SuggestionsResponse)
def get_recipe_suggestions(
    min_match_percentage: float = Query(default=0.5, ge=0, le=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    pantry_items = db.query(PantryItem).all()
    pantry_ingredient_ids = {item.ingredient_id for item in pantry_items}

    recipes = (
        db.query(Recipe)
        .filter(Recipe.is_active.is_(True))
        .options(joinedload(Recipe.ingredients), joinedload(Recipe.images))
        .limit(500)
        .all()
    )

    suggestions = []
    for recipe in recipes:
        if not recipe.ingredients:
            continue

        total_ingredients = len(recipe.ingredients)
        available = [
            ri for ri in recipe.ingredients
            if ri.ingredient_id in pantry_ingredient_ids
        ]
        available_count = len(available)
        match_percentage = available_count / total_ingredients

        if match_percentage < min_match_percentage:
            continue

        missing = [
            MissingIngredient(
                ingredient_id=ri.ingredient_id,
                ingredient_name=ri.ingredient.name,
                required_quantity=float(ri.quantity) if ri.quantity else None,
                unit=ri.unit,
            )
            for ri in recipe.ingredients
            if ri.ingredient_id not in pantry_ingredient_ids
        ]

        primary_image = next(
            (img for img in recipe.images if img.is_primary),
            recipe.images[0] if recipe.images else None,
        )

        suggestions.append(
            RecipeSuggestion(
                recipe_id=recipe.id,
                recipe_title=recipe.title,
                primary_image_id=primary_image.id if primary_image else None,
                total_ingredients=total_ingredients,
                available_ingredients=available_count,
                missing_ingredients=missing,
                match_percentage=round(match_percentage * 100, 1),
            )
        )

    suggestions.sort(key=lambda s: s.match_percentage, reverse=True)
    return SuggestionsResponse(suggestions=suggestions[:limit])
