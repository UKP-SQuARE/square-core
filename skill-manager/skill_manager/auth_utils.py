from typing import Dict

import jwt
from bson import ObjectId
from fastapi.exceptions import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from square_auth.auth import Auth
from starlette.requests import Request

from skill_manager import mongo_client
from skill_manager.models import Skill


def has_auth_header(request: Request) -> bool:
    return request.headers.get("Authorization", "").lower().startswith("bearer")


def get_payload_from_token(request: Request) -> Dict[str, str]:
    scheme, token = get_authorization_scheme_param(request.headers.get("Authorization"))
    assert scheme.lower() == "bearer", f"Only bearer auth is supported. Got {scheme}."
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)

    return {"realm": realm, "username": payload["preferred_username"]}


def get_skill_if_authorized(
    request: Request, skill_id: str, write_access: bool
) -> Skill:
    if has_auth_header(request):
        payload = get_payload_from_token(request)
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
