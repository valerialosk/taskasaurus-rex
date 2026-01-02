import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import get_db
from app.main import app
from app.models import Base  # импортируем все модели


@pytest.fixture(scope="function")
def test_db():
    """Создает чистую БД для каждого теста"""
    # используем in-memory SQLite с StaticPool для избежания threading issues
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # создаем таблицы
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = testing_session_local()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    # очистка после теста
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
