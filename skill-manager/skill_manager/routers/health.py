import logging
from typing import Dict

import requests
from fastapi import APIRouter, Depends, Path, Request
from square_skill_api.models.heartbeat import HeartbeatResult

from skill_manager.auth_utils import get_skill_if_authorized
from skill_manager.models import Skill
from skill_manager.routers import client_credentials
from skill_manager.settings import SkillManagerSettings

logger = logging.getLogger(__name__)

settings = SkillManagerSettings()
router = APIRouter(prefix="/health")


@router.get(
    "/heartbeat",
    response_model=HeartbeatResult,
)
async def heartbeat():
    """Checks if the skill-manager instance is up and running."""
    return HeartbeatResult(is_alive=True)


@router.get("/{id}/heartbeat", response_model=HeartbeatResult)
async def skill_heartbeat(
    request: Request,
    skill_id: str = Path(alias="id"),
    token: str = Depends(client_credentials),
):
    """Checks if a skill is up and running."""
    logger.debug(f"Checking skill health: {skill_id}")
    skill: Skill = get_skill_if_authorized(
        request, skill_id=skill_id, write_access=False
    )
    logger.info(f"Checking skill health: {skill.url}")
    try:
        skill_heartbeat_response = requests.get(
            f"{skill.url}/health/heartbeat",
            headers={"Authorization": f"Bearer {token}"},
        )
        skill_heartbeat_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.debug(
            "An exception occured while requesting skill health. {}".format(str(e))
        )
        return HeartbeatResult(is_alive=False)

    logger.debug("skill heartbeat response: {}".format(skill_heartbeat_response.text))
    return HeartbeatResult(is_alive=True)


@router.get(
    "/{id}/heartbeat-models",
    response_model=Dict[str, HeartbeatResult],
)
async def heartbeat_models(
    request: Request,
    skill_id: str = Path(alias="id"),
    token: str = Depends(client_credentials),
):
    """Checks if the models the skill uses are up and running."""

    skill: Skill = get_skill_if_authorized(
        request, skill_id=skill_id, write_access=False
    )
    model_status = {}
    for model in skill.models:
        url = f"{settings.square_url}/api/{model}/health/heartbeat"
        try:
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            model_status[model] = HeartbeatResult(is_alive=True)
        except requests.exceptions.RequestException as e:
            logger.debug(
                f"An exception occured requesting the health of {model} at {url}. "
                f"Error: {str(e)}"
            )
            model_status[model] = HeartbeatResult(is_alive=True)

    return model_status
