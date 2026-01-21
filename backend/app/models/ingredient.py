from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func

from app.core import Base, IngredientCategory


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(Enum(IngredientCategory), default=IngredientCategory.OTHER)
    default_unit = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
