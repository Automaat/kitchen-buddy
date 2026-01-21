from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core import get_db
from app.models import MealPlan, Recipe
from app.schemas import (
    MealPlanCreate,
    MealPlanResponse,
    MealPlanUpdate,
    WeekMealPlanResponse,
)

router = APIRouter()


def get_meal_plan_response(meal: MealPlan) -> dict:
    primary_image = next((img for img in meal.recipe.images if img.is_primary), None)
    if not primary_image and meal.recipe.images:
        primary_image = meal.recipe.images[0]

    return {
        "id": meal.id,
        "date": meal.date,
        "meal_type": meal.meal_type,
        "recipe_id": meal.recipe_id,
        "servings": meal.servings,
        "notes": meal.notes,
        "is_completed": meal.is_completed,
        "recipe": {
            "id": meal.recipe.id,
            "title": meal.recipe.title,
            "primary_image_id": primary_image.id if primary_image else None,
        },
        "created_at": meal.created_at,
        "updated_at": meal.updated_at,
    }


@router.get("/week/{week_date}", response_model=WeekMealPlanResponse)
def get_week_meal_plans(week_date: date, db: Session = Depends(get_db)):
    start = week_date - timedelta(days=week_date.weekday())
    end = start + timedelta(days=6)

    meals = (
        db.query(MealPlan)
        .options(joinedload(MealPlan.recipe).joinedload(Recipe.images))
        .filter(MealPlan.date >= start, MealPlan.date <= end)
        .order_by(MealPlan.date, MealPlan.meal_type)
        .all()
    )

    return WeekMealPlanResponse(
        start_date=start,
        end_date=end,
        meals=[MealPlanResponse(**get_meal_plan_response(m)) for m in meals],
    )


@router.post("", response_model=MealPlanResponse, status_code=201)
def create_meal_plan(meal_plan: MealPlanCreate, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).options(joinedload(Recipe.images)).filter(Recipe.id == meal_plan.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_meal = MealPlan(**meal_plan.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)

    db_meal.recipe = recipe
    return get_meal_plan_response(db_meal)


@router.put("/{meal_plan_id}", response_model=MealPlanResponse)
def update_meal_plan(
    meal_plan_id: int, meal_plan: MealPlanUpdate, db: Session = Depends(get_db)
):
    db_meal = (
        db.query(MealPlan)
        .options(joinedload(MealPlan.recipe).joinedload(Recipe.images))
        .filter(MealPlan.id == meal_plan_id)
        .first()
    )
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    update_data = meal_plan.model_dump(exclude_unset=True)

    if "recipe_id" in update_data:
        recipe = db.query(Recipe).options(joinedload(Recipe.images)).filter(Recipe.id == update_data["recipe_id"]).first()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

    for key, value in update_data.items():
        setattr(db_meal, key, value)

    db.commit()
    db.refresh(db_meal)

    return get_meal_plan_response(db_meal)


@router.delete("/{meal_plan_id}", status_code=204)
def delete_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    db_meal = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    db.delete(db_meal)
    db.commit()


@router.post("/copy-week")
def copy_week(source_date: date, target_date: date, db: Session = Depends(get_db)):
    source_start = source_date - timedelta(days=source_date.weekday())
    source_end = source_start + timedelta(days=6)
    target_start = target_date - timedelta(days=target_date.weekday())

    source_meals = (
        db.query(MealPlan)
        .filter(MealPlan.date >= source_start, MealPlan.date <= source_end)
        .all()
    )

    created = []
    for meal in source_meals:
        day_offset = (meal.date - source_start).days
        new_date = target_start + timedelta(days=day_offset)

        new_meal = MealPlan(
            date=new_date,
            meal_type=meal.meal_type,
            recipe_id=meal.recipe_id,
            servings=meal.servings,
            notes=meal.notes,
        )
        db.add(new_meal)
        created.append(new_meal)

    db.commit()
    return {"copied": len(created)}
