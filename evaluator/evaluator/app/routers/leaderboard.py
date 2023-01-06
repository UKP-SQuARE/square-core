import logging
from typing import Dict, List

import jwt
import requests
from fastapi import APIRouter, Depends, Request
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.models import DataSet, MetricResult
from evaluator.app.routers import client_credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/leaderboard")
auth = Auth()


@router.get(
    "/{dataset_name}/{metric_name}",
    response_model=List,
)
async def get_leaderboard(
    request: Request,
    dataset_name: str,
    metric_name: str,
    token: str = Depends(client_credentials),
):
    """
    Retrieves leaderboard data.

    Args:
        dataset_name (str): Name of the dataset to show leaderboard for.
        metric_name (str): Name of the metric to show leaderboard for.

    Returns: List of leaderboard entries.
    """
    user_id = get_user_id(request, token)

    # retrieve all evaluations for the respective dataset and metric
    dataset_filter = {"dataset_name": dataset_name.lower()}
    metric_filter = {"metrics." + metric_name.lower(): {"$exists": True}}
    results = mongo_client.client.evaluator.results.find(
        {"$and": [dataset_filter, metric_filter]}
    )
    metric_results = [MetricResult.from_mongo(result) for result in results]

    # retrieve skills
    skills = get_skills(token)

    # extract the information required for the leaderboard
    leaderboard = []
    for metric_result in metric_results:
        skill_id = str(metric_result.skill_id)

        if not skill_id in skills:
            continue

        is_private = skills[skill_id]["published"] is False
        has_access = not is_private or skills[skill_id]["user_id"] == user_id
        if not has_access:
            continue

        metric = metric_result.metrics[metric_name]
        leaderboard.append(
            {
                "rank": None,
                "date": metric["last_updated_at"],
                "skill_id": skill_id,
                "skill_name": skills[skill_id]["name"],
                "private": is_private,
                "result": metric["results"],
            }
        )
    # rank the results
    leaderboard = rank(leaderboard)
    return leaderboard


def rank(leaderboard):
    """
    Assigns a rank to each leaderboard entry.

    Args:
        leaderboard (List[dict]): List of leaderboard entries.

    Returns: List of leaderboard entries with assigned "rank" field.
    """
    if len(leaderboard) <= 0:
        return leaderboard

    key = get_ranking_key(leaderboard[0])

    leaderboard.sort(key=lambda x: x["result"][key], reverse=True)
    for i in range(0, len(leaderboard)):
        leaderboard[i]["rank"] = i + 1

    return leaderboard


def get_ranking_key(leaderboard_entry):
    """
    Determines the field that should be used to determine the final ranking.

    Args:
        leaderboard_entry (dict): A single entry of the leaderboard list.

    Returns: The key of the field that should be used to determine the ranking.
    """
    if (
        len(leaderboard_entry["result"].keys()) > 1
        and "f1" in leaderboard_entry["result"].keys()
    ):
        # multiple computed values => choose F1 for ranking (if exists)
        return "f1"
    else:
        # only one computed value (or no F1 available) => choose first (and usually only) one for ranking
        return leaderboard_entry["result"].keys()[0]


def get_skills(token: str) -> dict:
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"http://square-core-skill-manager-1:8000/api/skill", headers=headers
    )

    skills = dict()
    for skill in response.json():
        skills[skill["id"]] = skill

    return skills


def get_user_id(request: Request, token: str):
    if request.headers.get("Authorization", "").lower().startswith("bearer"):
        payload = jwt.decode(token, options=dict(verify_signature=False))
        user_id = payload["preferred_username"]
    else:
        user_id = None

    return user_id
