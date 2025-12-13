from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.tasks_router import router as tasks_router
from app.routes.categories_router import router as categories_router
from app.routes.calendar_router import router as calendar_router

app = FastAPI(
    title="Taskasaurus Rex",
    description="Task Scheduler Service API",
    version="0.1.0",
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


@app.get("/")
async def root():
    return {"message": "Taskasaurus Rex API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

