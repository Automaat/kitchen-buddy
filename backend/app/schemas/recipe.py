from __future__ import annotations

import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

from app.core import DietaryTag, DifficultyLevel

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
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class RecipeNoteResponse(BaseModel):
    id: int
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class RecipeBase(BaseModel):
    title: str
    description: str | None = None
    instructions: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int = 4
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    dietary_tags: list[DietaryTag] = []
    source_url: str | None = None

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("source_url must use http or https scheme")
        return v


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
    dietary_tags: list[DietaryTag] | None = None
    source_url: str | None = None
    is_active: bool | None = None
    ingredients: list[RecipeIngredientCreate] | None = None
    tag_ids: list[int] | None = None

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("source_url must use http or https scheme")
        return v


class RecipeListResponse(BaseModel):
    id: int
    title: str
    description: str | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    servings: int
    difficulty: DifficultyLevel
    dietary_tags: list[DietaryTag]
    is_favorite: bool
    primary_image_id: int | None
    tags: list[TagResponse]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class RecipeResponse(RecipeBase):
    id: int
    is_active: bool
    is_favorite: bool
    ingredients: list[RecipeIngredientResponse]
    images: list[RecipeImageResponse]
    tags: list[TagResponse]
    notes: list[RecipeNoteResponse]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class ScaledIngredientResponse(BaseModel):
    ingredient_id: int
    ingredient_name: str
    original_quantity: str | None
    scaled_quantity: str | None
    unit: str | None
    notes: str | None


class RecipeImportRequest(BaseModel):
    url: str


class RecipeImportResponse(BaseModel):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int | None = None
    ingredients: list[str] = []
    image_url: str | None = None
    source_url: str
