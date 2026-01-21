from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core import Base


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    recipes = relationship(
        "Recipe", secondary="recipe_collections", back_populates="collections"
    )


class RecipeCollection(Base):
    __tablename__ = "recipe_collections"

    recipe_id = Column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )
    collection_id = Column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    added_at = Column(DateTime, server_default=func.now())
