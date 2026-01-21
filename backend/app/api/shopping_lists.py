from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core import get_db
from app.models import Ingredient, MealPlan, RecipeIngredient, ShoppingList, ShoppingListItem
from app.schemas import (
    GenerateShoppingListRequest,
    ShoppingListCreate,
    ShoppingListItemCreate,
    ShoppingListItemResponse,
    ShoppingListResponse,
)

router = APIRouter()


def get_shopping_list_response(shopping_list: ShoppingList) -> dict:
    return {
        "id": shopping_list.id,
        "name": shopping_list.name,
        "start_date": shopping_list.start_date,
        "end_date": shopping_list.end_date,
        "is_active": shopping_list.is_active,
        "items": [
            ShoppingListItemResponse(
                id=item.id,
                ingredient_id=item.ingredient_id,
                name=item.name or (item.ingredient.name if item.ingredient else None),
                quantity=item.quantity,
                unit=item.unit,
                is_checked=item.is_checked,
                added_manually=item.added_manually,
                category=item.ingredient.category if item.ingredient else None,
                created_at=item.created_at,
            )
            for item in shopping_list.items
        ],
        "created_at": shopping_list.created_at,
        "updated_at": shopping_list.updated_at,
    }


@router.get("", response_model=list[ShoppingListResponse])
def list_shopping_lists(
    skip: int = 0, limit: int = 20, active_only: bool = True, db: Session = Depends(get_db)
):
    query = db.query(ShoppingList).options(
        joinedload(ShoppingList.items).joinedload(ShoppingListItem.ingredient)
    )
    if active_only:
        query = query.filter(ShoppingList.is_active.is_(True))

    lists = query.order_by(ShoppingList.created_at.desc()).offset(skip).limit(limit).all()
    return [ShoppingListResponse(**get_shopping_list_response(sl)) for sl in lists]


@router.post("", response_model=ShoppingListResponse, status_code=201)
def create_shopping_list(shopping_list: ShoppingListCreate, db: Session = Depends(get_db)):
    db_list = ShoppingList(**shopping_list.model_dump())
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return get_shopping_list_response(db_list)


@router.get("/{list_id}", response_model=ShoppingListResponse)
def get_shopping_list(list_id: int, db: Session = Depends(get_db)):
    shopping_list = (
        db.query(ShoppingList)
        .options(joinedload(ShoppingList.items).joinedload(ShoppingListItem.ingredient))
        .filter(ShoppingList.id == list_id)
        .first()
    )
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return get_shopping_list_response(shopping_list)


@router.delete("/{list_id}", status_code=204)
def delete_shopping_list(list_id: int, db: Session = Depends(get_db)):
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    db.delete(shopping_list)
    db.commit()


@router.post("/generate", response_model=ShoppingListResponse, status_code=201)
def generate_shopping_list(request: GenerateShoppingListRequest, db: Session = Depends(get_db)):
    meals = (
        db.query(MealPlan)
        .options(joinedload(MealPlan.recipe).joinedload(RecipeIngredient.ingredient))
        .filter(MealPlan.date >= request.start_date, MealPlan.date <= request.end_date)
        .all()
    )

    ingredient_totals: dict[int, dict] = defaultdict(
        lambda: {"quantity": 0, "unit": None, "ingredient": None}
    )

    for meal in meals:
        scale = meal.servings / meal.recipe.servings if meal.recipe.servings else 1
        for ri in meal.recipe.ingredients:
            ing_id = ri.ingredient_id
            ingredient_totals[ing_id]["ingredient"] = ri.ingredient

            if ri.quantity:
                try:
                    qty = float(ri.quantity) * scale
                    ingredient_totals[ing_id]["quantity"] += qty
                except ValueError:
                    pass

            if ri.unit and not ingredient_totals[ing_id]["unit"]:
                ingredient_totals[ing_id]["unit"] = ri.unit

    db_list = ShoppingList(
        name=request.name,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    db.add(db_list)
    db.flush()

    for ing_id, data in ingredient_totals.items():
        item = ShoppingListItem(
            shopping_list_id=db_list.id,
            ingredient_id=ing_id,
            quantity=str(round(data["quantity"], 2)) if data["quantity"] else None,
            unit=data["unit"],
        )
        db.add(item)

    db.commit()
    db.refresh(db_list)

    return get_shopping_list(db_list.id, db)


@router.post("/{list_id}/items", response_model=ShoppingListItemResponse, status_code=201)
def add_shopping_list_item(
    list_id: int, item: ShoppingListItemCreate, db: Session = Depends(get_db)
):
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    db_item = ShoppingListItem(
        shopping_list_id=list_id,
        ingredient_id=item.ingredient_id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        added_manually=True,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    ingredient = None
    if db_item.ingredient_id:
        ingredient = db.query(Ingredient).filter(Ingredient.id == db_item.ingredient_id).first()

    return ShoppingListItemResponse(
        id=db_item.id,
        ingredient_id=db_item.ingredient_id,
        name=db_item.name or (ingredient.name if ingredient else None),
        quantity=db_item.quantity,
        unit=db_item.unit,
        is_checked=db_item.is_checked,
        added_manually=db_item.added_manually,
        category=ingredient.category if ingredient else None,
        created_at=db_item.created_at,
    )


@router.post("/{list_id}/items/{item_id}/toggle", response_model=ShoppingListItemResponse)
def toggle_shopping_list_item(list_id: int, item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient))
        .filter(ShoppingListItem.id == item_id, ShoppingListItem.shopping_list_id == list_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_checked = not item.is_checked
    db.commit()
    db.refresh(item)

    return ShoppingListItemResponse(
        id=item.id,
        ingredient_id=item.ingredient_id,
        name=item.name or (item.ingredient.name if item.ingredient else None),
        quantity=item.quantity,
        unit=item.unit,
        is_checked=item.is_checked,
        added_manually=item.added_manually,
        category=item.ingredient.category if item.ingredient else None,
        created_at=item.created_at,
    )


@router.delete("/{list_id}/items/{item_id}", status_code=204)
def delete_shopping_list_item(list_id: int, item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(ShoppingListItem)
        .filter(ShoppingListItem.id == item_id, ShoppingListItem.shopping_list_id == list_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
