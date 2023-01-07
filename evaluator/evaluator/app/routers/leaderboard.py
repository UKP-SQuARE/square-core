import logging
import os
from typing import Dict, List

import jwt
import requests
from fastapi import APIRouter, Depends, Request
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.models import DataSet, LeaderboardEntry, Metric, MetricResult
from evaluator.app.routers import client_credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/leaderboard")
auth = Auth()
SKILL_MANAGER_API_URL = os.getenv(
    "SKILL_MANAGER_API_URL", "https://square.ukp-lab.de/api/skill-manager"
)


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
    # retrieve all evaluations for the respective dataset and metric
    dataset_filter = {"dataset_name": dataset_name.lower()}
    metric_filter = {"metrics." + metric_name.lower(): {"$exists": True}}
    results = mongo_client.client.evaluator.results.find(
        {"$and": [dataset_filter, metric_filter]}
    )
    metric_results = [MetricResult.from_mongo(result) for result in results]

    # retrieve user-id and skills
    user_id = get_user_id(request, token)
    skills = get_skills(token)

    # extract the information required for the leaderboard
    leaderboard = []
    for metric_result in metric_results:
        skill_id = str(metric_result.skill_id)

        if not skill_id in skills:
            continue

        skill_is_private = skills[skill_id]["published"] is False
        has_access = not skill_is_private or skills[skill_id]["user_id"] == user_id
        if not has_access:
            continue

        metric = Metric.parse_obj(metric_result.metrics[metric_name])
        leaderboard_entry = LeaderboardEntry(
            date=metric.last_updated_at,
            skill_id=skill_id,
            skill_name=skills[skill_id]["name"],
            private=skill_is_private,
            result=metric.results,
        )
        leaderboard.append(leaderboard_entry)

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
    # get key of the field we want to base the rank on
    key = get_ranking_key(leaderboard[0])
    # sort by that field
    leaderboard.sort(key=lambda x: x.result[key], reverse=True)
    # assign ranks
    prev_value = None
    rank = 0
    for i in range(0, len(leaderboard)):
        current_value = leaderboard[i].result[key]
        if current_value != prev_value:
            # only assign the next rank if the results are different (if they are the same, both entries will simply have the same rank)
            prev_value = current_value
            rank = rank + 1
        leaderboard[i].rank = rank
    return leaderboard


def get_ranking_key(leaderboard_entry):
    """
    Determines the field that should be used to determine the final ranking.

    Args:
        leaderboard_entry (dict): A single entry of the leaderboard list.

    Returns: The key of the field that should be used to determine the ranking.
    """
    if (
        len(leaderboard_entry.result.keys()) > 1
        and "f1" in leaderboard_entry.result.keys()
    ):
        # multiple computed values => choose F1 for ranking (if exists)
        return "f1"
    else:
        # only one computed value (or no F1 available) => choose first (and usually only) one for ranking
        return list(leaderboard_entry.result.keys())[0]


def get_skills(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(f"{SKILL_MANAGER_API_URL}/skill", headers=headers)

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
