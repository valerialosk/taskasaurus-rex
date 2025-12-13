from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session, selectinload

from app.models import Task, TaskStatus, TaskPriority


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[List[Task], int]:
        query = select(Task).options(selectinload(Task.category))

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if category_id:
            query = query.where(Task.category_id == category_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )
        if date_from:
            query = query.where(Task.due_date >= date_from)
        if date_to:
            query = query.where(Task.due_date <= date_to)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query)

        sort_column = getattr(Task, sort_by, Task.created_at)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def get_task(self, task_id: int) -> Optional[Task]:
        query = select(Task).where(Task.id == task_id).options(
            selectinload(Task.category),
            selectinload(Task.subtasks)
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        status: str = "pending",
        category_id: Optional[int] = None,
        due_date: Optional[datetime] = None,
        parent_id: Optional[int] = None,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=TaskPriority(priority),
            status=TaskStatus(status),
            category_id=category_id,
            due_date=due_date,
            parent_id=parent_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    async def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        due_date: Optional[datetime] = None,
    ) -> Optional[Task]:
        task = await self.get_task(task_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = TaskPriority(priority)
        if status is not None:
            task.status = TaskStatus(status)
        if category_id is not None:
            task.category_id = category_id
        if due_date is not None:
            task.due_date = due_date

        self.db.commit()
        self.db.refresh(task)
        return task

    async def update_task_status(self, task_id: int, status: str) -> Optional[Task]:
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = TaskStatus(status)
        self.db.commit()
        self.db.refresh(task)
        return task

    async def delete_task(self, task_id: int) -> bool:
        task = await self.get_task(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    async def get_subtasks(self, task_id: int) -> List[Task]:
        query = select(Task).where(Task.parent_id == task_id)
        result = self.db.execute(query)
        return result.scalars().all()

    async def duplicate_task(self, task_id: int) -> Optional[Task]:
        original = await self.get_task(task_id)
        if not original:
            return None

        duplicate = Task(
            title=f"{original.title} (копия)",
            description=original.description,
            priority=original.priority,
            status=TaskStatus.PENDING,
            category_id=original.category_id,
            due_date=original.due_date,
            parent_id=original.parent_id,
        )
        self.db.add(duplicate)
        self.db.commit()
        self.db.refresh(duplicate)
        return duplicate

    async def get_overdue_tasks(self, skip: int = 0, limit: int = 100) -> tuple[List[Task], int]:
        now = datetime.now()
        query = select(Task).where(
            and_(
                Task.due_date < now,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
            )
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query)

        query = query.order_by(Task.due_date.asc()).offset(skip).limit(limit)
        result = self.db.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def get_upcoming_tasks(
        self, 
        days: int = 7, 
        priority: Optional[str] = None
    ) -> List[Task]:
        now = datetime.now()
        future = now + timedelta(days=days)
        
        query = select(Task).where(
            and_(
                Task.due_date >= now,
                Task.due_date <= future,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
            )
        )

        if priority:
            query = query.where(Task.priority == priority)

        query = query.order_by(Task.due_date.asc())
        result = self.db.execute(query)
        return result.scalars().all()

    async def get_tasks_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Task]:
        query = select(Task).where(
            and_(
                Task.due_date >= start_date,
                Task.due_date <= end_date
            )
        ).order_by(Task.due_date.asc())

        result = self.db.execute(query)
        return result.scalars().all()

