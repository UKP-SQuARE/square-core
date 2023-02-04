import logging
from typing import Dict

import jwt
from bson import ObjectId
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from square_auth.auth import Auth
from starlette.requests import Request

from evaluator.app import mongo_client

logger = logging.getLogger(__name__)


def has_auth_header(request: Request) -> bool:
    return request.headers.get("Authorization", "").lower().startswith("bearer")


async def get_payload_from_token(request: Request) -> Dict[str, str]:
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)

    return {"realm": realm, "username": payload["preferred_username"]}


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
