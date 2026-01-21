from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core import get_db
from app.models import Favorite, Recipe
from app.schemas import FavoriteResponse, RecipeListResponse

router = APIRouter()


@router.get("", response_model=list[RecipeListResponse])
def list_favorites(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    favorites = (
        db.query(Favorite)
        .options(
            joinedload(Favorite.recipe).joinedload(Recipe.tags),
            joinedload(Favorite.recipe).joinedload(Recipe.images),
        )
        .order_by(Favorite.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        RecipeListResponse(
            id=f.recipe.id,
            title=f.recipe.title,
            description=f.recipe.description,
            prep_time_minutes=f.recipe.prep_time_minutes,
            cook_time_minutes=f.recipe.cook_time_minutes,
            servings=f.recipe.servings,
            difficulty=f.recipe.difficulty,
            dietary_tags=f.recipe.dietary_tags or [],
            is_favorite=True,
            primary_image_id=next(
                (img.id for img in f.recipe.images if img.is_primary),
                f.recipe.images[0].id if f.recipe.images else None,
            ),
            tags=f.recipe.tags,
            created_at=f.recipe.created_at,
        )
        for f in favorites
        if f.recipe.is_active
    ]


@router.post("/{recipe_id}", response_model=FavoriteResponse, status_code=201)
def add_favorite(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    existing = db.query(Favorite).filter(Favorite.recipe_id == recipe_id).first()
    if existing:
        return existing

    db_favorite = Favorite(recipe_id=recipe_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


@router.delete("/{recipe_id}", status_code=204)
def remove_favorite(recipe_id: int, db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter(Favorite.recipe_id == recipe_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
