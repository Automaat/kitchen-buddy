from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import get_db
from app.models import Ingredient
from app.schemas import IngredientCreate, IngredientUpdate, IngredientResponse

router = APIRouter()


@router.get("", response_model=list[IngredientResponse])
def list_ingredients(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    query = db.query(Ingredient)
    if active_only:
        query = query.filter(Ingredient.is_active.is_(True))
    if search:
        query = query.filter(Ingredient.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=IngredientResponse, status_code=201)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    existing = db.query(Ingredient).filter(Ingredient.name == ingredient.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient already exists")

    db_ingredient = Ingredient(**ingredient.model_dump())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int, ingredient: IngredientUpdate, db: Session = Depends(get_db)
):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    for key, value in ingredient.model_dump(exclude_unset=True).items():
        setattr(db_ingredient, key, value)

    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@router.delete("/{ingredient_id}", status_code=204)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db_ingredient.is_active = False
    db.commit()
