from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.core import MealType


class MealPlanBase(BaseModel):
    date: date
    meal_type: MealType
    recipe_id: int
    servings: int = 4
    notes: str | None = None


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanUpdate(BaseModel):
    date: date | None = None
    meal_type: MealType | None = None
    recipe_id: int | None = None
    servings: int | None = None
    notes: str | None = None
    is_completed: bool | None = None


class RecipeSummary(BaseModel):
    id: int
    title: str
    primary_image_id: int | None

    model_config = {"from_attributes": True}


class MealPlanResponse(MealPlanBase):
    id: int
    is_completed: bool
    recipe: RecipeSummary
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WeekMealPlanResponse(BaseModel):
    start_date: date
    end_date: date
    meals: list[MealPlanResponse]
