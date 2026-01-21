from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core import DifficultyLevel

from .tag import TagResponse


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: str | None = None
    unit: str | None = None
    notes: str | None = None


class RecipeIngredientResponse(BaseModel):
    id: int
    ingredient_id: int
    ingredient_name: str
    quantity: str | None
    unit: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class RecipeImageResponse(BaseModel):
    id: int
    is_primary: bool
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeBase(BaseModel):
    title: str
    description: str | None = None
    instructions: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int = 4
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class RecipeCreate(RecipeBase):
    ingredients: list[RecipeIngredientCreate] = []
    tag_ids: list[int] = []


class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int | None = None
    difficulty: DifficultyLevel | None = None
    is_active: bool | None = None
    ingredients: list[RecipeIngredientCreate] | None = None
    tag_ids: list[int] | None = None


class RecipeListResponse(BaseModel):
    id: int
    title: str
    description: str | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    servings: int
    difficulty: DifficultyLevel
    is_favorite: bool
    primary_image_id: int | None
    tags: list[TagResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeResponse(RecipeBase):
    id: int
    is_active: bool
    is_favorite: bool
    ingredients: list[RecipeIngredientResponse]
    images: list[RecipeImageResponse]
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScaledIngredientResponse(BaseModel):
    ingredient_id: int
    ingredient_name: str
    original_quantity: str | None
    scaled_quantity: str | None
    unit: str | None
    notes: str | None
