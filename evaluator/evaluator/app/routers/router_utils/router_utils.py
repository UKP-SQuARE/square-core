import logging
import os
from typing import Dict

import requests
from fastapi.exceptions import HTTPException

logger = logging.getLogger(__name__)
SKILL_MANAGER_API_URL = os.getenv(
    "SKILL_MANAGER_API_URL", "https://square.ukp-lab.de/api/skill-manager"
)


def validate_access(token_payload: Dict):
    """
    Function to validate access. Currently SQuARE has no user roles, so we check for the statically defined user names.
    """
    ALLOWED_USER_NAMES = ["ukp", "local_square_user"]
    try:
        if token_payload["username"].lower() not in ALLOWED_USER_NAMES:
            logger.info(f'Access denied for user_name={token_payload["username"]}')
            raise KeyError
        logger.info(f'Access granted for user_name={token_payload["username"]}')
    except KeyError:
        raise HTTPException(403, "Forbidden.")


def get_skills(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(f"{SKILL_MANAGER_API_URL}/skill", headers=headers)

    skills = dict()
    for skill in response.json():
        skills[skill["id"]] = skill

    return skills
