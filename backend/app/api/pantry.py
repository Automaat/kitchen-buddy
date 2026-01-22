from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import get_db
from app.models import Ingredient, PantryItem
from app.schemas import PantryItemCreate, PantryItemUpdate, PantryItemResponse

router = APIRouter()


def get_pantry_item_response(item: PantryItem) -> dict:
    return {
        "id": item.id,
        "ingredient_id": item.ingredient_id,
        "quantity": item.quantity,
        "unit": item.unit,
        "expiration_date": item.expiration_date,
        "notes": item.notes,
        "ingredient_name": item.ingredient.name,
        "ingredient_category": item.ingredient.category,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@router.get("", response_model=list[PantryItemResponse])
def list_pantry_items(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(PantryItem)
    if search:
        query = query.join(Ingredient).filter(Ingredient.name.ilike(f"%{search}%"))
    items = query.offset(skip).limit(limit).all()
    return [get_pantry_item_response(item) for item in items]


@router.post("", response_model=PantryItemResponse, status_code=201)
def create_pantry_item(item: PantryItemCreate, db: Session = Depends(get_db)):
    ingredient = db.query(Ingredient).filter(Ingredient.id == item.ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=400, detail="Ingredient not found")

    db_item = PantryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return get_pantry_item_response(db_item)


@router.get("/{item_id}", response_model=PantryItemResponse)
def get_pantry_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return get_pantry_item_response(item)


@router.put("/{item_id}", response_model=PantryItemResponse)
def update_pantry_item(
    item_id: int, item: PantryItemUpdate, db: Session = Depends(get_db)
):
    db_item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return get_pantry_item_response(db_item)


@router.delete("/{item_id}", status_code=204)
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    db.delete(db_item)
    db.commit()


@router.post("/add-ingredient/{ingredient_id}", response_model=PantryItemResponse, status_code=201)
def add_ingredient_to_pantry(
    ingredient_id: int,
    quantity: float,
    unit: str | None = None,
    db: Session = Depends(get_db),
):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=400, detail="Ingredient not found")

    existing = (
        db.query(PantryItem)
        .filter(PantryItem.ingredient_id == ingredient_id)
        .first()
    )
    if existing:
        existing.quantity = existing.quantity + quantity
        db.commit()
        db.refresh(existing)
        return get_pantry_item_response(existing)

    db_item = PantryItem(
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit or ingredient.default_unit,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return get_pantry_item_response(db_item)
