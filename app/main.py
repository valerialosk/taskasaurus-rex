from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
from app.models.base import Base
from app.routes.calendar_router import router as calendar_router
from app.routes.categories_router import router as categories_router
from app.routes.tasks_router import router as tasks_router

# создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Taskasaurus Rex",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(categories_router)
app.include_router(calendar_router)


@app.get(
    "/",
    tags=["Root"],
    summary="Корневой endpoint",
    description="Возвращает информацию о API",
    response_description="Приветственное сообщение",
)
async def root():
    """
    Базовый endpoint для проверки работоспособности API.

    Возвращает:
    - **message**: Название API
    """
    return {"message": "Taskasaurus Rex API", "version": "0.1.0"}


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Проверка состояния сервиса",
    response_description="Статус работы сервиса",
)
async def health_check():
    """
    Endpoint для мониторинга состояния сервиса.

    Используется для:
    - Проверки доступности API
    - Интеграции с системами мониторинга
    - Load balancer health checks

    Возвращает:
    - **status**: Текущее состояние сервиса
    """
    return {"status": "healthy", "service": "taskasaurus-rex"}
