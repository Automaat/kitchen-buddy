from pydantic import BaseModel

from .meal_plan import MealPlanResponse


class DashboardResponse(BaseModel):
    total_recipes: int
    total_ingredients: int
    total_favorites: int
    todays_meals: list[MealPlanResponse]
