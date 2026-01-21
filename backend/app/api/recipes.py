import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.core import DietaryTag, DifficultyLevel, get_db
from app.models import Ingredient, Recipe, RecipeImage, RecipeIngredient, RecipeNote, Tag
from app.schemas import (
    RecipeCreate,
    RecipeListResponse,
    RecipeResponse,
    RecipeUpdate,
    RecipeImageResponse,
    RecipeIngredientResponse,
    RecipeNoteResponse,
    ScaledIngredientResponse,
    RecipeImportRequest,
    RecipeImportResponse,
    RecipeNoteCreate,
    RecipeNoteSchemaResponse,
)
from app.utils import scale_quantity, import_recipe_from_url

logger = logging.getLogger(__name__)

router = APIRouter()


def get_recipe_response(recipe: Recipe) -> dict:
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "prep_time_minutes": recipe.prep_time_minutes,
        "cook_time_minutes": recipe.cook_time_minutes,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "dietary_tags": recipe.dietary_tags or [],
        "source_url": recipe.source_url,
        "is_active": recipe.is_active,
        "is_favorite": recipe.favorite is not None,
        "ingredients": [
            RecipeIngredientResponse(
                id=ri.id,
                ingredient_id=ri.ingredient_id,
                ingredient_name=ri.ingredient.name,
                quantity=ri.quantity,
                unit=ri.unit,
                notes=ri.notes,
            )
            for ri in recipe.ingredients
        ],
        "images": [RecipeImageResponse.model_validate(img) for img in recipe.images],
        "tags": recipe.tags,
        "notes": [RecipeNoteResponse.model_validate(n) for n in recipe.notes],
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
    }


@router.get("", response_model=list[RecipeListResponse])
def list_recipes(
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    difficulty: DifficultyLevel | None = None,
    tag_ids: list[int] = Query(default=[]),
    dietary_tags: list[DietaryTag] = Query(default=[]),
    favorites_only: bool = False,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Recipe)
        .options(joinedload(Recipe.tags), joinedload(Recipe.images), joinedload(Recipe.favorite))
        .filter(Recipe.is_active.is_(True))
    )

    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if tag_ids:
        query = query.filter(Recipe.tags.any(Tag.id.in_(tag_ids)))
    if favorites_only:
        query = query.filter(Recipe.favorite.has())

    recipes = query.order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()

    if dietary_tags:
        requested_tags = {tag.value for tag in dietary_tags}
        recipes = [
            r for r in recipes
            if r.dietary_tags and requested_tags.issubset(set(r.dietary_tags))
        ]

    return [
        RecipeListResponse(
            id=r.id,
            title=r.title,
            description=r.description,
            prep_time_minutes=r.prep_time_minutes,
            cook_time_minutes=r.cook_time_minutes,
            servings=r.servings,
            difficulty=r.difficulty,
            dietary_tags=r.dietary_tags or [],
            is_favorite=r.favorite is not None,
            primary_image_id=next((img.id for img in r.images if img.is_primary), r.images[0].id if r.images else None),
            tags=r.tags,
            created_at=r.created_at,
        )
        for r in recipes
    ]


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = Recipe(
        title=recipe.title,
        description=recipe.description,
        instructions=recipe.instructions,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        servings=recipe.servings,
        difficulty=recipe.difficulty,
        dietary_tags=[tag.value for tag in recipe.dietary_tags],
        source_url=recipe.source_url,
    )

    for ri in recipe.ingredients:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
        if not ingredient:
            raise HTTPException(status_code=400, detail=f"Ingredient {ri.ingredient_id} not found")
        db_recipe.ingredients.append(
            RecipeIngredient(
                ingredient_id=ri.ingredient_id,
                quantity=ri.quantity,
                unit=ri.unit,
                notes=ri.notes,
            )
        )

    if recipe.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(recipe.tag_ids)).all()
        db_recipe.tags = tags

    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    return get_recipe_response(db_recipe)


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.images),
            joinedload(Recipe.tags),
            joinedload(Recipe.favorite),
            joinedload(Recipe.notes),
        )
        .filter(Recipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return get_recipe_response(recipe)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe: RecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.images),
            joinedload(Recipe.tags),
            joinedload(Recipe.favorite),
            joinedload(Recipe.notes),
        )
        .filter(Recipe.id == recipe_id)
        .first()
    )
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = recipe.model_dump(exclude_unset=True, exclude={"ingredients", "tag_ids", "dietary_tags"})
    for key, value in update_data.items():
        setattr(db_recipe, key, value)
    if recipe.dietary_tags is not None:
        db_recipe.dietary_tags = [tag.value for tag in recipe.dietary_tags]

    if recipe.ingredients is not None:
        db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id).delete()
        for ri in recipe.ingredients:
            db_recipe.ingredients.append(
                RecipeIngredient(
                    ingredient_id=ri.ingredient_id,
                    quantity=ri.quantity,
                    unit=ri.unit,
                    notes=ri.notes,
                )
            )

    if recipe.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(recipe.tag_ids)).all()
        db_recipe.tags = tags

    db.commit()
    db.refresh(db_recipe)

    return get_recipe_response(db_recipe)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_recipe.is_active = False
    db.commit()


@router.post("/{recipe_id}/images", response_model=RecipeImageResponse, status_code=201)
async def upload_recipe_image(
    recipe_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    if is_primary:
        db.query(RecipeImage).filter(
            RecipeImage.recipe_id == recipe_id, RecipeImage.is_primary.is_(True)
        ).update({"is_primary": False})

    max_order = (
        db.query(RecipeImage)
        .filter(RecipeImage.recipe_id == recipe_id)
        .count()
    )

    db_image = RecipeImage(
        recipe_id=recipe_id,
        data=content,
        mime_type=file.content_type,
        is_primary=is_primary,
        sort_order=max_order,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return db_image


@router.get("/{recipe_id}/scale/{servings}", response_model=list[ScaledIngredientResponse])
def scale_recipe(recipe_id: int, servings: int, db: Session = Depends(get_db)):
    recipe = (
        db.query(Recipe)
        .options(joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient))
        .filter(Recipe.id == recipe_id)
        .first()
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return [
        ScaledIngredientResponse(
            ingredient_id=ri.ingredient_id,
            ingredient_name=ri.ingredient.name,
            original_quantity=ri.quantity,
            scaled_quantity=scale_quantity(ri.quantity, recipe.servings, servings),
            unit=ri.unit,
            notes=ri.notes,
        )
        for ri in recipe.ingredients
    ]


@router.post("/import", response_model=RecipeImportResponse)
async def import_recipe(request: RecipeImportRequest):
    try:
        data = await import_recipe_from_url(request.url)
        return RecipeImportResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to import recipe from %s", request.url)
        raise HTTPException(status_code=400, detail="Failed to import recipe from URL")


@router.post("/{recipe_id}/notes", response_model=RecipeNoteSchemaResponse, status_code=201)
def add_recipe_note(recipe_id: int, note: RecipeNoteCreate, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_note = RecipeNote(recipe_id=recipe_id, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.put("/{recipe_id}/notes/{note_id}", response_model=RecipeNoteSchemaResponse)
def update_recipe_note(
    recipe_id: int, note_id: int, note: RecipeNoteCreate, db: Session = Depends(get_db)
):
    db_note = (
        db.query(RecipeNote)
        .filter(RecipeNote.id == note_id, RecipeNote.recipe_id == recipe_id)
        .first()
    )
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/{recipe_id}/notes/{note_id}", status_code=204)
def delete_recipe_note(recipe_id: int, note_id: int, db: Session = Depends(get_db)):
    db_note = (
        db.query(RecipeNote)
        .filter(RecipeNote.id == note_id, RecipeNote.recipe_id == recipe_id)
        .first()
    )
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
