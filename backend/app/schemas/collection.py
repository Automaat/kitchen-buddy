from datetime import datetime

from pydantic import BaseModel


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None


class CollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CollectionRecipeSummary(BaseModel):
    id: int
    title: str
    primary_image_id: int | None

    model_config = {"from_attributes": True}


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    recipe_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CollectionDetailResponse(CollectionResponse):
    recipes: list[CollectionRecipeSummary]
