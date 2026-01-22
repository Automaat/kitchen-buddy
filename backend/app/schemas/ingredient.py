from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.core import IngredientCategory


class NutritionInfo(BaseModel):
    calories: Decimal | None = None
    protein: Decimal | None = None
    carbs: Decimal | None = None
    fat: Decimal | None = None
    fiber: Decimal | None = None


class IngredientBase(BaseModel):
    name: str
    category: IngredientCategory = IngredientCategory.OTHER
    default_unit: str | None = None


class IngredientCreate(IngredientBase):
    calories: Decimal | None = None
    protein: Decimal | None = None
    carbs: Decimal | None = None
    fat: Decimal | None = None
    fiber: Decimal | None = None
    cost_per_unit: Decimal | None = None


class IngredientUpdate(BaseModel):
    name: str | None = None
    category: IngredientCategory | None = None
    default_unit: str | None = None
    is_active: bool | None = None
    calories: Decimal | None = None
    protein: Decimal | None = None
    carbs: Decimal | None = None
    fat: Decimal | None = None
    fiber: Decimal | None = None
    cost_per_unit: Decimal | None = None


class IngredientResponse(IngredientBase):
    id: int
    is_active: bool
    calories: Decimal | None = None
    protein: Decimal | None = None
    carbs: Decimal | None = None
    fat: Decimal | None = None
    fiber: Decimal | None = None
    cost_per_unit: Decimal | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
