import logging
from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter

from evaluator.app.models import TaskResponse
from evaluator.tasks.celery import app as celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task")


@router.get("", name="Get current tasks")
async def get_tasks():
    # https://docs.celeryq.dev/en/latest/userguide/workers.html#inspecting-workers
    i = celery_app.control.inspect()
    scheduled = i.scheduled()
    active = i.active()
    reserved = i.reserved()

    tasks = {
        "scheduled": scheduled,
        "active": active,
        "reserved": reserved,
    }
    logger.info("/tasks: {}".format(tasks))

    return tasks


@router.get("/{task_id}", name="Get single task result")
async def get_task(task_id):
    task = AsyncResult(task_id)
    if not task.ready():
        return task_response(task)
    elif task.failed():
        error = task.get(propagate=False)
        logger.error(f"Task '{task_id}' failed: {error!r}")
        return task_response(task, f"{error}")
    else:
        result = task.get()
        return task_response(task, result)


def task_response(task, result=None) -> TaskResponse:
    return TaskResponse(
        task_id=str(task.id),
        state=task.state,
        finished=task.date_done,
        result=str(result) if not result is None else result,
    )
