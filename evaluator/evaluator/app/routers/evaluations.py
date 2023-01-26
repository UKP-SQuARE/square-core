import logging
import os
from typing import Dict, List

import jwt
import requests
from fastapi import APIRouter, Depends, Request
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.models import Evaluation, EvaluationResult, MetricResult
from evaluator.app.routers import client_credentials
from evaluator.auth_utils import (
    get_metrics_if_authorized,
    get_payload_from_token,
    has_auth_header,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluations")
auth = Auth()
SKILL_MANAGER_API_URL = os.getenv(
    "SKILL_MANAGER_API_URL", "https://square.ukp-lab.de/api/skill-manager"
)


@router.get(
    "",
    response_model=List[EvaluationResult],
)
async def get_evaluations(request: Request, token: str = Depends(client_credentials)):
    """Returns all skills that a user has access to. A user has access to
    all public skills, and private skill created by them."""

    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        user_id = payload["username"]

    evaluations = mongo_client.client.evaluator.results.find()
    evaluations = [MetricResult.from_mongo(e) for e in evaluations]
    evaluation_results = []

    evaluations_status = mongo_client.client.evaluator.evaluations.find()
    evaluations_status = [Evaluation.from_mongo(e) for e in evaluations]

    skills = get_skills(token)

    for evaluation in evaluations:
        skill_id = str(evaluation.skill_id)

        if not skill_id in skills:
            continue

        skill_is_public = skills[skill_id]["published"]
        has_access = skill_is_public or skills[skill_id]["user_id"] == user_id

        if not has_access:
            continue

        for (metric_name, metric_result) in evaluation.metrics.items():
            evaluation_results.append(
                EvaluationResult(
                    evaluation_id=skill_id + metric_name,
                    skill_name=skills[skill_id]["name"],
                    dataset=evaluation.dataset_name,
                    public=skill_is_public,
                    metric_name=metric_name,
                    metric_result=metric_result["results"],
                    skill_url=skills[skill_id]["url"],
                )
            )

    return evaluation_results


def get_skills(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(f"{SKILL_MANAGER_API_URL}/skill", headers=headers)

    skills = dict()
    for skill in response.json():
        skills[skill["id"]] = skill

    return skills
