from fastapi import APIRouter
from models.skill import Skill
from api.routes.utils import create_file_paths, run_tests
import json
#from explainability.worker.celery_app import run_checklist

router = APIRouter()

@router.post("/run-checklist", name="run-checklist")
async def run_checklist_tests(skill: Skill):
    """ Function for testing a Skill

    Takes an input of Skill class object and returns a json consisting 
    all the test cases and their prediction made by the specified skill

    Args:
        skill (Skill) : An object of class Skill
    
    Returns:
        json_data (json object) : A json object containing all the test cases and their predictions made by
            the specified skill

    """
    path = create_file_paths(skill.skill_id)
    json_data = run_tests(skill, path)
    
    
    return json_data
