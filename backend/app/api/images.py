from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core import get_db
from app.models import RecipeImage

router = APIRouter()


@router.get("/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(RecipeImage).filter(RecipeImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(content=image.data, media_type=image.mime_type)


@router.delete("/{image_id}", status_code=204)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(RecipeImage).filter(RecipeImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(image)
    db.commit()
