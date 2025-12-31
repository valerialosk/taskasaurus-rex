from datetime import date

from fastapi import APIRouter

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/month")
async def get_month_calendar(year: int, month: int):
    return {"year": year, "month": month, "days": {}, "total_tasks": 0}


@router.get("/week")
async def get_week_calendar(date: date):
    return {"week_start": date, "week_end": date, "days": [], "total_tasks": 0}


@router.get("/day")
async def get_day_calendar(date: date):
    return {"date": date, "tasks": [], "total_tasks": 0}


@router.get("/today")
async def get_today_tasks():
    return {"date": date.today(), "tasks": [], "total_tasks": 0}


@router.get("/overdue")
async def get_overdue_tasks():
    return {"tasks": [], "total_overdue": 0}
