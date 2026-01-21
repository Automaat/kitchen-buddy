from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core import get_db
from app.models import Favorite, Ingredient, MealPlan, Recipe
from app.schemas import DashboardResponse, MealPlanResponse

router = APIRouter()


@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    total_recipes = db.query(Recipe).filter(Recipe.is_active.is_(True)).count()
    total_ingredients = db.query(Ingredient).filter(Ingredient.is_active.is_(True)).count()
    total_favorites = db.query(Favorite).count()

    today = date.today()
    todays_meals = (
        db.query(MealPlan)
        .options(joinedload(MealPlan.recipe).joinedload(Recipe.images))
        .filter(MealPlan.date == today)
        .order_by(MealPlan.meal_type)
        .all()
    )

    meals_response = []
    for meal in todays_meals:
        primary_image = next((img for img in meal.recipe.images if img.is_primary), None)
        if not primary_image and meal.recipe.images:
            primary_image = meal.recipe.images[0]

        meals_response.append(
            MealPlanResponse(
                id=meal.id,
                date=meal.date,
                meal_type=meal.meal_type,
                recipe_id=meal.recipe_id,
                servings=meal.servings,
                notes=meal.notes,
                is_completed=meal.is_completed,
                recipe={
                    "id": meal.recipe.id,
                    "title": meal.recipe.title,
                    "primary_image_id": primary_image.id if primary_image else None,
                },
                created_at=meal.created_at,
                updated_at=meal.updated_at,
            )
        )

    return DashboardResponse(
        total_recipes=total_recipes,
        total_ingredients=total_ingredients,
        total_favorites=total_favorites,
        todays_meals=meals_response,
    )
