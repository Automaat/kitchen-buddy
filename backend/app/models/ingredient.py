from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, Numeric, String, func

from app.core import Base, IngredientCategory


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(Enum(IngredientCategory), default=IngredientCategory.OTHER)
    default_unit = Column(String(50))
    is_active = Column(Boolean, default=True)

    # Nutritional info (per 100g)
    calories = Column(Numeric(10, 2))
    protein = Column(Numeric(10, 2))
    carbs = Column(Numeric(10, 2))
    fat = Column(Numeric(10, 2))
    fiber = Column(Numeric(10, 2))

    # Cost info
    cost_per_unit = Column(Numeric(10, 2))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
