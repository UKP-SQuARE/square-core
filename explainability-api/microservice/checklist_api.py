import requests
import json
from fastapi import APIRouter
from typing import List

import checklist

router = APIRouter()

# Dev purpose hard coded
with open("../checklists/extractive_model_tests.json") as f:
    extractive_model_tests = json.load(f)


@router.get('/')
def read_root():
    return {"Hello": "World"}


@router.get('/checklist/{skill_id}', name="run checklist")
def run_checklist(skill_id: str, n: int = None) -> list:
    # tested with this skill_id: 63cdbd06a8b0d566ef20cb54
    try:
        skill_response = requests.get(f'https://square.ukp-lab.de/api/skill-manager/skill/{skill_id}')
        skill = skill_response.json()
        skill_id = skill["id"]
        skill_type = skill["skill_type"]

        test_cases = extractive_model_tests['tests']
        model_inputs = checklist.create_query(skill, test_cases)

        if n is not None:
            model_inputs['request'] = model_inputs["request"][:n]  # if all would be too much
        else:
            model_inputs['request'] = model_inputs["request"]  # if all would be too much
        model_outputs = checklist.predict(model_inputs, skill_id)
        
        return model_outputs  
    
    except Exception as e:
        print(e)
