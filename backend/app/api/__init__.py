from fastapi import APIRouter

from .ingredients import router as ingredients_router
from .recipes import router as recipes_router
from .tags import router as tags_router
from .meal_plans import router as meal_plans_router
from .shopping_lists import router as shopping_lists_router
from .favorites import router as favorites_router
from .dashboard import router as dashboard_router
from .images import router as images_router
from .collections import router as collections_router

api_router = APIRouter()
api_router.include_router(ingredients_router, prefix="/ingredients", tags=["ingredients"])
api_router.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
api_router.include_router(tags_router, prefix="/tags", tags=["tags"])
api_router.include_router(meal_plans_router, prefix="/meal-plans", tags=["meal-plans"])
api_router.include_router(shopping_lists_router, prefix="/shopping-lists", tags=["shopping-lists"])
api_router.include_router(favorites_router, prefix="/favorites", tags=["favorites"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
api_router.include_router(collections_router, prefix="/collections", tags=["collections"])
