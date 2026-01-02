from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    categories, total = await service.get_categories(skip=skip, limit=limit)
    return {
        "categories": [CategoryResponse.model_validate(c) for c in categories],
        "total": total,
    }


@router.get("/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.post("", status_code=201)
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    category = await service.create_category(category_data)
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}")
async def update_category(
    category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)
):
    service = CategoryService(db)
    category = await service.update_category(category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    success = await service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"deleted": True}
