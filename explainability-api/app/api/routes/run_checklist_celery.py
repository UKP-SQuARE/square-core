from fastapi import APIRouter
from worker.checklist_tasks import run_checklist
from models.skill import Skill
from models.task import Task
from api.routes.utils_celery import create_file_paths, get_json_data

import json

router = APIRouter()

@router.post("/celery-run-checklist", name="celery-run-checklist")
def run_checklist_celery(skill : Skill):
    """ Function for testing a Skill with celery

    Takes an input of Skill class object and returns a dictionary with the following attributes-
        - message : a message
        - task_id : ID of the task
        - task_state : state of the task

    Args:
        skill (Skill) : An object of class Skill
    
    Returns:
        dictionary (dict) : A dictionary containing three attributes -
            - message : a message
            - task_id : ID of the task
            - task_state : state of the task
    """

    file_directory = create_file_paths(skill.skill_id) 
    json_data = get_json_data(file_directory, skill.skill_type)

    data = {
        "base_model" : skill.skill_base_model,
        "adapter" : skill.skill_adapter,
        "json_data" : json_data,
        "skill_query_path" : skill.skill_query_path
    }
    task = run_checklist.delay(data)

    return {"message": "Task Has Started to Execute",
            "task_id": str(task.task_id),
            "task_state": str(task.state)}
