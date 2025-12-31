from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("")
async def get_tasks(
    # TODO: добавить параметры
):
    return {"tasks": [], "total": 0}


@router.get("/{task_id}")
async def get_task(task_id: int):
    return {"id": task_id, "title": "Task", "status": "pending"}


@router.post("")
async def create_task(
    title: str,
    status: str = "pending",
):
    return {"id": 1, "title": title, "status": status}


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    title: str | None = None,
):
    return {"id": task_id, "title": title}


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    return {"deleted": True}


@router.post("/{task_id}/duplicate")
async def duplicate_task(task_id: int):
    return {"id": task_id + 1000, "title": "Copy"}
