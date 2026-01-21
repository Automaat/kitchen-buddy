from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.core import IngredientCategory


class ShoppingListItemCreate(BaseModel):
    ingredient_id: int | None = None
    name: str | None = None
    quantity: str | None = None
    unit: str | None = None


class ShoppingListItemResponse(BaseModel):
    id: int
    ingredient_id: int | None
    name: str | None
    quantity: str | None
    unit: str | None
    is_checked: bool
    added_manually: bool
    category: IngredientCategory | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ShoppingListBase(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None


class ShoppingListCreate(ShoppingListBase):
    pass


class ShoppingListResponse(ShoppingListBase):
    id: int
    is_active: bool
    items: list[ShoppingListItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerateShoppingListRequest(BaseModel):
    name: str
    start_date: date
    end_date: date
