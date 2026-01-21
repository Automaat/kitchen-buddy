from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.core import Base, DietaryTag, DifficultyLevel


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    recipes = relationship("Recipe", secondary="recipe_tags", back_populates="tags")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    prep_time_minutes = Column(Integer)
    cook_time_minutes = Column(Integer)
    servings = Column(Integer, default=4)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    dietary_tags = Column(ARRAY(Enum(DietaryTag, name="dietarytag")), default=[])
    source_url = Column(String(2048))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ingredients = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    images = relationship(
        "RecipeImage", back_populates="recipe", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary="recipe_tags", back_populates="recipes")
    meal_plans = relationship("MealPlan", back_populates="recipe")
    favorite = relationship(
        "Favorite", back_populates="recipe", uselist=False, cascade="all, delete-orphan"
    )
    collections = relationship(
        "Collection", secondary="recipe_collections", back_populates="recipes"
    )
    notes = relationship(
        "RecipeNote", back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity = Column(String(50))
    unit = Column(String(50))
    notes = Column(String(255))

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")


class RecipeImage(Base):
    __tablename__ = "recipe_images"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    data = Column(LargeBinary, nullable=False)
    mime_type = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    recipe = relationship("Recipe", back_populates="images")


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    recipe_id = Column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
