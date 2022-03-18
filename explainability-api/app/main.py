from typing import Optional
from fastapi import FastAPI
import requests
import json
from .models import Skill, Query, SkillModelAdapter

app = FastAPI()


@app.get("/")
async def check_health():
    return "Api is running"


@app.post("/test")
async def test_skill(skill: Skill):
    query = {
            "query": "Sophie is happy, right?",
            "skill_args": {
                "context": "Sophie is very joyful. Florence is very organised.",
                "base_model": "bert-base-uncased",
                "adapter": "AdapterHub/bert-base-uncased-pf-boolq",
            },
            "num_results": 1,
            "user_id": "ukp"
    }
    headers = {'Content-type': 'application/json'}
    json_object = json.dumps(query)
    request_path = "https://square.ukp-lab.de/api/skill-manager/skill/61a9f66935adbbf1f2433077/query"
    response = requests.post(request_path, data = json_object, headers = headers)
    predictions = response.json()
    return predictions

@app.post("/predict")
async def predict(query: Query):
    return "from predict function"
