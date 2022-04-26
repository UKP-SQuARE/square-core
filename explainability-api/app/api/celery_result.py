from fastapi import APIRouter
from tasks.tasks import run_checklist
from celery.result import AsyncResult

router = APIRouter()

@router.get("/celery-result/{task_id}", name="celery-task-result")
def get_task_result(task_id:str):
    """Function to return the task state

    This function returns the task state if the state is SUCCESS then returns the result

    Args:

        task_id (str): ID of the task 

    Returns:

        The state of task if the task finished then returns the result
    
    """

    task = run_checklist.AsyncResult(task_id)
    if  str(task.state) == "SUCCESS":
        result = task.get()
        return result
    elif str(task.state) == "PENDING":
        return "Working on"
    else:
        return "Failed"