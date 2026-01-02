from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("")
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    tasks, total = await service.get_tasks(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category_id=category_id,
        search=search,
    )
    return {"tasks": [TaskResponse.model_validate(t) for t in tasks], "total": total}


@router.get("/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.post("", status_code=201)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = await service.create_task(task_data)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}")
async def update_task(
    task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)
):
    service = TaskService(db)
    task = await service.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    success = await service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


@router.post("/{task_id}/duplicate", status_code=201)
async def duplicate_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    duplicate = await service.duplicate_task(task_id)
    if not duplicate:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(duplicate)
