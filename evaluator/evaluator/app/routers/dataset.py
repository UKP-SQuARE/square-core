import logging
from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter

from evaluator.app.models import DataSet
from evaluator.tasks import tasks
from evaluator.tasks.celery import app as celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dataset")


@router.get(
    "",
    response_model=List[str],
)
async def get_datasets():
    """Returns a list of supported data sets."""
    datasets = [dataset.value for dataset in DataSet]

    logger.debug("get_datasets {datasets}".format(datasets=datasets))
    return datasets


@router.get("/start-task", name="")
async def start_test_task():
    res = tasks.test_something.delay()
    return res.id


@router.get("/show-tasks", name="")
async def get_all_tasks():
    # https://docs.celeryq.dev/en/latest/userguide/workers.html#inspecting-workers
    i = celery_app.control.inspect()
    # Show the items that have an ETA or are scheduled for later processing
    scheduled = i.scheduled()

    # Show tasks that are currently active.
    active = i.active()

    # Show tasks that have been claimed by workers
    reserved = i.reserved()

    tasks = {
        "scheduled": scheduled,
        "active": active,
        "reserved": reserved,
    }

    logger.info("/tasks: {}".format(tasks))

    return tasks


@router.get("/task_result/{task_id}", name="")
async def get_task_status(task_id):
    task = AsyncResult(task_id)
    if task.failed():
        return "Task failed"
    if not task.ready():
        return "Task still processing"
    result = task.get()
    return {"task_id": str(task.id), "finished": str(task.date_done), "result": result}
