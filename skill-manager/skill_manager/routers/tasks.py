from fastapi import APIRouter, Path
from celery.result import AsyncResult
from skill_manager.models.task import TaskResult, TaskStatus

router = APIRouter(prefix="/tasks")

@router.get("/{id}/status", response_model=TaskStatus)
def get_task_status(task_id = Path(..., alias="id")):
    result = AsyncResult(task_id)
    return TaskStatus(task_id=task_id, status=result.status)

@router.get("/{id}/result", response_model=TaskResult)
def get_task_result(task_id=Path(..., alias="id")):
    result = AsyncResult(task_id)
    return TaskResult(task_id=task_id, result=result.get())
