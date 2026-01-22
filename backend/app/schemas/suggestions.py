from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class MissingIngredient(BaseModel):
    ingredient_id: int
    ingredient_name: str
    required_quantity: Decimal | None
    unit: str | None


class RecipeSuggestion(BaseModel):
    recipe_id: int
    recipe_title: str
    primary_image_id: int | None
    total_ingredients: int
    available_ingredients: int
    missing_ingredients: list[MissingIngredient]
    match_percentage: float


class SuggestionsResponse(BaseModel):
    suggestions: list[RecipeSuggestion]
