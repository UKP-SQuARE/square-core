import requests
import json
from fastapi import APIRouter
from typing import List

import checklist

router = APIRouter()

# Dev purpose
with open("../checklists/extractive_model_tests.json") as f:
    extractive_model_tests = json.load(f)


@router.get('/checklist/{skill_id}', name="run checklist", response_model=List)
def run_checklist(skill_id: str) -> list:
    # async def run_checklist(skill_id, test_cases: List = None) -> list:
    # test id: '63a6246c2e30fd4c06f7a0be'
    try:
        skill = requests.get(f'https://square.ukp-lab.de/api/skill-manager/skill/{skill_id}')

        skill_id = skill["id"]
        skill_type = skill["skill_type"]

        test_cases = extractive_model_tests['tests']
        model_inputs = checklist.create_query(skill, test_cases)
        # get predictions
        model_outputs = checklist.predict(model_inputs, skill_id)
        return model_outputs
    except Exception as e:
        print(e)
