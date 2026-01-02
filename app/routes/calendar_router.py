from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import TaskResponse
from app.services.calendar_service import CalendarService
from app.services.task_service import TaskService

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/month")
async def get_month_calendar(year: int, month: int, db: Session = Depends(get_db)):
    service = CalendarService(db)
    calendar = await service.get_month_calendar(year, month)
    return calendar


@router.get("/week")
async def get_week_calendar(target_date: date, db: Session = Depends(get_db)):
    service = CalendarService(db)
    calendar = await service.get_week_calendar(target_date)
    return calendar


@router.get("/day")
async def get_day_calendar(target_date: date, db: Session = Depends(get_db)):
    service = CalendarService(db)
    tasks_data = await service.get_day_tasks(target_date)
    return tasks_data


@router.get("/today")
async def get_today_tasks(db: Session = Depends(get_db)):
    service = CalendarService(db)
    tasks_data = await service.get_day_tasks(date.today())
    return tasks_data


@router.get("/overdue")
async def get_overdue_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    tasks, total = await service.get_overdue_tasks(skip=skip, limit=limit)
    return {
        "tasks": [TaskResponse.model_validate(t) for t in tasks],
        "total_overdue": total,
    }
