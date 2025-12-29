from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
async def get_categories():
    return {"categories": [], "total": 0}


@router.get("/{category_id}")
async def get_category(category_id: int):
    return {"id": category_id, "name": "Category"}


@router.post("")
async def create_category(
    name: str,
    color: str = "#808080",
):
    return {"id": 1, "name": name, "color": color}


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    name: Optional[str] = None,
):
    return {"id": category_id, "name": name}


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    return {"deleted": True}
