from typing import Dict

import jwt
from bson import ObjectId
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from skill_manager import mongo_client
from skill_manager.models import Skill
from square_auth.auth import Auth
from starlette.requests import Request


def has_auth_header(request: Request) -> bool:
    return request.headers.get("Authorization", "").lower().startswith("bearer")


async def get_payload_from_token(request: Request) -> Dict[str, str]:
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)

    return {"realm": realm, "username": payload["preferred_username"]}


async def get_skill_if_authorized(
    request: Request, skill_id: str, write_access: bool
) -> Skill:
    if has_auth_header(request):
        payload = await get_payload_from_token(request)
    else:
        payload = {"username": None}

    skill = Skill.from_mongo(
        mongo_client.client.skill_manager.skills.find_one({"_id": ObjectId(skill_id)})
    )
    if skill is None:
        raise HTTPException(404, "Skill not found.")
    skill_by_user = skill.user_id == payload["username"]
    if skill_by_user or (not write_access and skill.published):
        return skill
    else:
        raise HTTPException(403)
