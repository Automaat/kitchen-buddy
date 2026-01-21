from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core import Base


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship(
        "ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan"
    )


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(
        Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE")
    )
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="SET NULL"))
    name = Column(String(255))
    quantity = Column(String(50))
    unit = Column(String(50))
    is_checked = Column(Boolean, default=False)
    added_manually = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    shopping_list = relationship("ShoppingList", back_populates="items")
    ingredient = relationship("Ingredient")
