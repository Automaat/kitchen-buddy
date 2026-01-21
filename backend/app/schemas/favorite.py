from datetime import datetime

from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    id: int
    recipe_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
