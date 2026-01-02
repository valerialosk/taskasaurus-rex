from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Category, Task


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    async def get_categories(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Category], int]:
        query = select(Category)

        count_query = select(func.count()).select_from(Category)
        total = self.db.scalar(count_query)

        query = query.order_by(Category.created_at.desc()).offset(skip).limit(limit)
        result = self.db.execute(query)
        categories = result.scalars().all()

        return categories, total

    async def get_category(self, category_id: int) -> Category | None:
        query = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.tasks))
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_category(self, category_data) -> Category:
        category = Category(
            name=category_data.name,
            color=category_data.color if category_data.color else "#808080",
            icon=category_data.icon,
            description=category_data.description,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    async def update_category(self, category_id: int, category_data) -> Category | None:
        category = await self.get_category(category_id)
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    async def delete_category(
        self, category_id: int, reassign_to: int | None = None
    ) -> bool:
        category = await self.get_category(category_id)
        if not category:
            return False

        if reassign_to:
            query = select(Task).where(Task.category_id == category_id)
            result = self.db.execute(query)
            tasks = result.scalars().all()
            for task in tasks:
                task.category_id = reassign_to
        else:
            query = select(Task).where(Task.category_id == category_id)
            result = self.db.execute(query)
            tasks = result.scalars().all()
            for task in tasks:
                task.category_id = None

        self.db.delete(category)
        self.db.commit()
        return True

    async def get_category_tasks(
        self, category_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Task], int]:
        query = select(Task).where(Task.category_id == category_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query)

        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = self.db.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def get_category_stats(self, category_id: int) -> dict:
        query = select(Task).where(Task.category_id == category_id)
        result = self.db.execute(query)
        tasks = result.scalars().all()

        stats = {
            "category_id": category_id,
            "total_tasks": len(tasks),
            "by_status": {
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "cancelled": 0,
            },
            "by_priority": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "urgent": 0,
            },
        }

        for task in tasks:
            stats["by_status"][task.status.value] += 1
            stats["by_priority"][task.priority.value] += 1

        return stats
