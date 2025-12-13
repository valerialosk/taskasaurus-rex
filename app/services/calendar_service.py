from typing import List, Dict
from datetime import datetime, date, timedelta
from calendar import monthrange
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus


class CalendarService:
    def __init__(self, db: Session):
        self.db = db

    async def get_month_calendar(self, year: int, month: int) -> dict:
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])

        query = select(Task).where(
            and_(
                Task.due_date >= first_day,
                Task.due_date <= last_day
            )
        ).order_by(Task.due_date.asc())

        result = self.db.execute(query)
        tasks = result.scalars().all()

        days_dict = {}
        for task in tasks:
            if task.due_date:
                day_key = task.due_date.date().isoformat()
                if day_key not in days_dict:
                    days_dict[day_key] = []
                days_dict[day_key].append(task)

        return {
            "year": year,
            "month": month,
            "days": days_dict,
            "total_tasks": len(tasks),
        }

    async def get_week_calendar(self, target_date: date) -> dict:
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)

        query = select(Task).where(
            and_(
                Task.due_date >= week_start,
                Task.due_date <= week_end
            )
        ).order_by(Task.due_date.asc())

        result = self.db.execute(query)
        tasks = result.scalars().all()

        days = []
        current_day = week_start
        while current_day <= week_end:
            day_tasks = [t for t in tasks if t.due_date and t.due_date.date() == current_day]
            days.append({
                "date": current_day.isoformat(),
                "tasks": day_tasks,
                "count": len(day_tasks)
            })
            current_day += timedelta(days=1)

        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "days": days,
            "total_tasks": len(tasks),
        }

    async def get_day_calendar(self, target_date: date) -> dict:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        query = select(Task).where(
            and_(
                Task.due_date >= start_datetime,
                Task.due_date <= end_datetime
            )
        ).order_by(Task.due_date.asc())

        result = self.db.execute(query)
        tasks = result.scalars().all()

        return {
            "date": target_date.isoformat(),
            "tasks": tasks,
            "total_tasks": len(tasks),
        }

    async def get_calendar_range(
        self, 
        start_date: date, 
        end_date: date, 
        group_by: str = "day"
    ) -> dict:
        query = select(Task).where(
            and_(
                Task.due_date >= start_date,
                Task.due_date <= end_date
            )
        ).order_by(Task.due_date.asc())

        result = self.db.execute(query)
        tasks = result.scalars().all()

        groups = []
        if group_by == "day":
            current = start_date
            while current <= end_date:
                day_tasks = [t for t in tasks if t.due_date and t.due_date.date() == current]
                groups.append({
                    "date": current.isoformat(),
                    "tasks": day_tasks,
                    "count": len(day_tasks)
                })
                current += timedelta(days=1)
        elif group_by == "week":
            current = start_date
            while current <= end_date:
                week_end = min(current + timedelta(days=6), end_date)
                week_tasks = [
                    t for t in tasks 
                    if t.due_date and current <= t.due_date.date() <= week_end
                ]
                groups.append({
                    "week_start": current.isoformat(),
                    "week_end": week_end.isoformat(),
                    "tasks": week_tasks,
                    "count": len(week_tasks)
                })
                current = week_end + timedelta(days=1)
        elif group_by == "month":
            current_month = start_date.replace(day=1)
            while current_month <= end_date:
                month_end = date(
                    current_month.year, 
                    current_month.month, 
                    monthrange(current_month.year, current_month.month)[1]
                )
                month_tasks = [
                    t for t in tasks 
                    if t.due_date and current_month <= t.due_date.date() <= month_end
                ]
                groups.append({
                    "month": f"{current_month.year}-{current_month.month:02d}",
                    "tasks": month_tasks,
                    "count": len(month_tasks)
                })
                if current_month.month == 12:
                    current_month = date(current_month.year + 1, 1, 1)
                else:
                    current_month = date(current_month.year, current_month.month + 1, 1)

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "group_by": group_by,
            "groups": groups,
            "total_tasks": len(tasks),
        }

    async def get_today_tasks(self) -> dict:
        return await self.get_day_calendar(date.today())

    async def get_calendar_stats(self, start_date: date, end_date: date) -> dict:
        created_query = select(Task).where(
            and_(
                func.date(Task.created_at) >= start_date,
                func.date(Task.created_at) <= end_date
            )
        )
        created_result = self.db.execute(created_query)
        created_tasks = created_result.scalars().all()

        completed_query = select(Task).where(
            and_(
                Task.status == TaskStatus.COMPLETED,
                func.date(Task.updated_at) >= start_date,
                func.date(Task.updated_at) <= end_date
            )
        )
        completed_result = self.db.execute(completed_query)
        completed_tasks = completed_result.scalars().all()

        daily_stats = []
        current = start_date
        while current <= end_date:
            created_count = len([
                t for t in created_tasks 
                if t.created_at and t.created_at.date() == current
            ])
            completed_count = len([
                t for t in completed_tasks 
                if t.updated_at and t.updated_at.date() == current
            ])
            daily_stats.append({
                "date": current.isoformat(),
                "created": created_count,
                "completed": completed_count,
            })
            current += timedelta(days=1)

        total_created = len(created_tasks)
        total_completed = len(completed_tasks)
        completion_rate = (
            (total_completed / total_created * 100) 
            if total_created > 0 
            else 0.0
        )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_stats": daily_stats,
            "summary": {
                "total_created": total_created,
                "total_completed": total_completed,
                "completion_rate": round(completion_rate, 2),
            },
        }

