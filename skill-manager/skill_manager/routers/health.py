import logging
from urllib.parse import urljoin

import requests
from fastapi import APIRouter

from square_skill_api.models.heartbeat import HeartbeatResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health")

@router.get(
    "/heartbeat",
    response_model=HeartbeatResult,
)
async def heartbeat():
    """Checks if the skill-manager instance is still up and running."""
    return HeartbeatResult(is_alive=True)


@router.get(
    "/skill-heartbeat",
    response_model=HeartbeatResult,
)
async def skill_heartbeat(skill_url: str):
    """Checks if a skill is still up and running."""
    skill_health_url = urljoin(skill_url, "health/heartbeat")

    skill_heartbeat_response = requests.get(skill_health_url)
    logger.debug(
        "skill at {} health {}".format(
            skill_health_url, skill_heartbeat_response.json()
        )
    )

    return skill_heartbeat_response.json()
