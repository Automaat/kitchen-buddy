from datetime import datetime

from pydantic import BaseModel


class RecipeNoteCreate(BaseModel):
    content: str


class RecipeNoteUpdate(BaseModel):
    content: str


class RecipeNoteResponse(BaseModel):
    id: int
    recipe_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
