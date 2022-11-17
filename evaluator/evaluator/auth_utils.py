from typing import Dict

import jwt
from bson import ObjectId
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from square_auth.auth import Auth
from starlette.requests import Request

from evaluator import mongo_client
from evaluator.models import Example


def has_auth_header(request: Request) -> bool:
    return request.headers.get("Authorization", "").lower().startswith("bearer")


async def get_payload_from_token(request: Request) -> Dict[str, str]:
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)

    return {"realm": realm, "username": payload["preferred_username"]}


async def get_example_if_authorized(request: Request, exampleId: str) -> Example:
    if has_auth_header(request):
        payload = await get_payload_from_token(request)
    else:
        payload = {"username": None}

    example = Example.from_mongo(
        mongo_client.client.evaluator.example.find_one({"_id": ObjectId(exampleId)})
    )
    if example is None:
        raise HTTPException(404, "Example not found.")
    return example
