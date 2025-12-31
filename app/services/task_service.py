from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Task, TaskPriority, TaskStatus


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        priority: str | None = None,
        category_id: int | None = None,
        search: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Task], int]:
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
                    Task.description.ilike(search_pattern),
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

    async def get_task(self, task_id: int) -> Task | None:
        query = (
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.category), selectinload(Task.subtasks))
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_task(
        self,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        status: str = "pending",
        category_id: int | None = None,
        due_date: datetime | None = None,
        parent_id: int | None = None,
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
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        category_id: int | None = None,
        due_date: datetime | None = None,
    ) -> Task | None:
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

    async def update_task_status(self, task_id: int, status: str) -> Task | None:
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

    async def get_subtasks(self, task_id: int) -> list[Task]:
        query = select(Task).where(Task.parent_id == task_id)
        result = self.db.execute(query)
        return result.scalars().all()

    async def duplicate_task(self, task_id: int) -> Task | None:
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

    async def get_overdue_tasks(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Task], int]:
        now = datetime.now()
        query = select(Task).where(
            and_(
                Task.due_date < now,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
            )
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query)

        query = query.order_by(Task.due_date.asc()).offset(skip).limit(limit)
        result = self.db.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def get_upcoming_tasks(
        self, days: int = 7, priority: str | None = None
    ) -> list[Task]:
        now = datetime.now()
        future = now + timedelta(days=days)

        query = select(Task).where(
            and_(
                Task.due_date >= now,
                Task.due_date <= future,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
            )
        )

        if priority:
            query = query.where(Task.priority == priority)

        query = query.order_by(Task.due_date.asc())
        result = self.db.execute(query)
        return result.scalars().all()

    async def get_tasks_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[Task]:
        query = (
            select(Task)
            .where(and_(Task.due_date >= start_date, Task.due_date <= end_date))
            .order_by(Task.due_date.asc())
        )

        result = self.db.execute(query)
        return result.scalars().all()
