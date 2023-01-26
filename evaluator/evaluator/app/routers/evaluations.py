import logging
import os
from typing import Dict, List

import jwt
import requests
from fastapi import APIRouter, Depends, Request
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.models import (
    Evaluation,
    EvaluationResult,
    EvaluationStatus,
    MetricResult,
)
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

    metric_results = mongo_client.client.evaluator.results.find()
    metric_results = [MetricResult.from_mongo(e) for e in metric_results]
    results = []

    evaluations = mongo_client.client.evaluator.evaluations.find()
    evaluations = [Evaluation.from_mongo(e) for e in evaluations]

    skills = get_skills(token)

    for evaluation in evaluations:
        skill_id = str(evaluation.skill_id)

        if not skill_id in skills:
            continue

        skill_is_public = skills[skill_id]["published"]
        has_access = skill_is_public or skills[skill_id]["user_id"] == user_id

        if not has_access:
            continue

        if (
            evaluation.prediction_status is not EvaluationStatus.finished
            or evaluation.metric_status is not EvaluationStatus.finished
        ):
            if (
                evaluation.prediction_status is EvaluationStatus.failed
                or evaluation.metric_status is EvaluationStatus.failed
            ):
                status = "FAILED"
            else:
                status = "RUNNING"

            results.append(
                EvaluationResult(
                    evaluation_id=skill_id + evaluation.metric_name + status,
                    evaluation_status=status,
                    skill_name=skills[skill_id]["name"],
                    dataset=evaluation.dataset_name,
                    public=skill_is_public,
                    metric_name=evaluation.metric_name,
                    metric_result={"status": status},
                    skill_url=skills[skill_id]["url"],
                )
            )
            continue

        status = "FINISHED"
        metric_result = next(
            item
            for item in metric_results
            if str(item.skill_id) == skill_id
            and item.dataset_name == evaluation.dataset_name
        )

        for (metric_name, metric_data) in metric_result.metrics.items():
            if metric_name == evaluation.metric_name:
                results.append(
                    EvaluationResult(
                        evaluation_id=skill_id + metric_name + status,
                        evaluation_status=status,
                        skill_name=skills[skill_id]["name"],
                        dataset=metric_result.dataset_name,
                        public=skill_is_public,
                        metric_name=metric_name,
                        metric_result=metric_data["results"],
                        skill_url=skills[skill_id]["url"],
                    )
                )

    return results


def get_skills(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(f"{SKILL_MANAGER_API_URL}/skill", headers=headers)

    skills = dict()
    for skill in response.json():
        skills[skill["id"]] = skill

    return skills
