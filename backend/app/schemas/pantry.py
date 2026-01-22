from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core import IngredientCategory


class PantryItemBase(BaseModel):
    ingredient_id: int
    quantity: Decimal = Field(gt=0)
    unit: str | None = None
    expiration_date: datetime.date | None = None
    notes: str | None = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemUpdate(BaseModel):
    quantity: Decimal | None = None
    unit: str | None = None
    expiration_date: datetime.date | None = None
    notes: str | None = None


class PantryItemResponse(PantryItemBase):
    id: int
    ingredient_name: str
    ingredient_category: IngredientCategory
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class PantryIngredientSummary(BaseModel):
    ingredient_id: int
    ingredient_name: str
    category: IngredientCategory
    total_quantity: Decimal
    unit: str | None
