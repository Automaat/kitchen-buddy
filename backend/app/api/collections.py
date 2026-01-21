from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core import get_db
from app.models import Collection, Recipe, RecipeCollection
from app.schemas import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionDetailResponse,
    CollectionRecipeSummary,
)

router = APIRouter()


def get_primary_image_id(recipe: Recipe) -> int | None:
    if not recipe.images:
        return None
    primary = next((img for img in recipe.images if img.is_primary), None)
    return primary.id if primary else recipe.images[0].id


@router.get("", response_model=list[CollectionResponse])
def list_collections(db: Session = Depends(get_db)):
    collections = (
        db.query(Collection)
        .options(joinedload(Collection.recipes))
        .order_by(Collection.name)
        .all()
    )
    return [
        CollectionResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            recipe_count=len([r for r in c.recipes if r.is_active]),
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in collections
    ]


@router.post("", response_model=CollectionResponse, status_code=201)
def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
    db_collection = Collection(name=collection.name, description=collection.description)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return CollectionResponse(
        id=db_collection.id,
        name=db_collection.name,
        description=db_collection.description,
        recipe_count=0,
        created_at=db_collection.created_at,
        updated_at=db_collection.updated_at,
    )


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
def get_collection(collection_id: int, db: Session = Depends(get_db)):
    collection = (
        db.query(Collection)
        .options(joinedload(Collection.recipes).joinedload(Recipe.images))
        .filter(Collection.id == collection_id)
        .first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    active_recipes = [r for r in collection.recipes if r.is_active]
    return CollectionDetailResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        recipe_count=len(active_recipes),
        recipes=[
            CollectionRecipeSummary(
                id=r.id,
                title=r.title,
                primary_image_id=get_primary_image_id(r),
            )
            for r in active_recipes
        ],
        created_at=collection.created_at,
        updated_at=collection.updated_at,
    )


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int, collection: CollectionUpdate, db: Session = Depends(get_db)
):
    db_collection = (
        db.query(Collection)
        .options(joinedload(Collection.recipes))
        .filter(Collection.id == collection_id)
        .first()
    )
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if collection.name is not None:
        db_collection.name = collection.name
    if collection.description is not None:
        db_collection.description = collection.description

    db.commit()
    db.refresh(db_collection)
    return CollectionResponse(
        id=db_collection.id,
        name=db_collection.name,
        description=db_collection.description,
        recipe_count=len([r for r in db_collection.recipes if r.is_active]),
        created_at=db_collection.created_at,
        updated_at=db_collection.updated_at,
    )


@router.delete("/{collection_id}", status_code=204)
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    db_collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    db.delete(db_collection)
    db.commit()


@router.post("/{collection_id}/recipes/{recipe_id}", status_code=201)
def add_recipe_to_collection(
    collection_id: int, recipe_id: int, db: Session = Depends(get_db)
):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    existing = (
        db.query(RecipeCollection)
        .filter(
            RecipeCollection.collection_id == collection_id,
            RecipeCollection.recipe_id == recipe_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Recipe already in collection")

    db_entry = RecipeCollection(collection_id=collection_id, recipe_id=recipe_id)
    db.add(db_entry)
    db.commit()
    return {"message": "Recipe added to collection"}


@router.delete("/{collection_id}/recipes/{recipe_id}", status_code=204)
def remove_recipe_from_collection(
    collection_id: int, recipe_id: int, db: Session = Depends(get_db)
):
    entry = (
        db.query(RecipeCollection)
        .filter(
            RecipeCollection.collection_id == collection_id,
            RecipeCollection.recipe_id == recipe_id,
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Recipe not in collection")

    db.delete(entry)
    db.commit()
