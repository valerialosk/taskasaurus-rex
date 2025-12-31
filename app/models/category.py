from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), default="#808080")
    icon = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship(
        "Task", back_populates="category", cascade="all, delete-orphan"
    )
