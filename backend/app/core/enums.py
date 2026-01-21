from enum import Enum


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class IngredientCategory(str, Enum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    MEAT = "meat"
    SEAFOOD = "seafood"
    PANTRY = "pantry"
    FROZEN = "frozen"
    BAKERY = "bakery"
    BEVERAGES = "beverages"
    CONDIMENTS = "condiments"
    SPICES = "spices"
    OTHER = "other"
