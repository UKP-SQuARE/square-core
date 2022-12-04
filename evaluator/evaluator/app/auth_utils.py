from typing import Dict

import jwt
from bson import ObjectId
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from square_auth.auth import Auth
from starlette.requests import Request

from evaluator import mongo_client


def has_auth_header(request: Request) -> bool:
    return request.headers.get("Authorization", "").lower().startswith("bearer")


async def get_payload_from_token(request: Request) -> Dict[str, str]:
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)

    return {"realm": realm, "username": payload["preferred_username"]}
