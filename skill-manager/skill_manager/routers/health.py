import logging
from urllib.parse import urljoin

import requests
from fastapi import APIRouter, Depends
from square_skill_api.models.heartbeat import HeartbeatResult

from skill_manager.routers import client_credentials

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
async def skill_heartbeat(skill_url: str, token: str = Depends(client_credentials)):
    """Checks if a skill is still up and running."""
    skill_health_url = urljoin(skill_url, "health/heartbeat")

    skill_heartbeat_response = requests.get(
        skill_health_url, headers={"Authorization": f"Bearer {token}"}
    )
    logger.debug(
        "skill heartbeat response: {response}".format(skill_heartbeat_response.text)
    )
    return {"is_alive": skill_heartbeat_response.status_code == 200}
