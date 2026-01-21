from __future__ import annotations

import datetime

from pydantic import BaseModel

from app.core import IngredientCategory


class IngredientBase(BaseModel):
    name: str
    category: IngredientCategory = IngredientCategory.OTHER
    default_unit: str | None = None


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = None
    category: IngredientCategory | None = None
    default_unit: str | None = None
    is_active: bool | None = None


class IngredientResponse(IngredientBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
