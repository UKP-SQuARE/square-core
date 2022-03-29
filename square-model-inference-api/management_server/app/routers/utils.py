import jwt
from fastapi import Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

from square_auth.auth import Auth


async def get_payload_from_token(request: Request):
    http_bearer = HTTPBearer()
    auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
    token = auth_credentials.credentials
    payload = jwt.decode(token, options=dict(verify_signature=False))
    realm = Auth.get_realm_from_token(token)
    return {"realm": realm, "username": payload["preferred_username"]}


def has_auth_header(request: Request):
    return request.headers.get("Authorization", "").lower().startswith("bearer")


async def get_user_id(request: Request):
    """
    gets the id of the user that accesses a resource API
    """
    if has_auth_header(request):
        payload = await get_payload_from_token(request)
        user_id = payload["username"]
    else:
        user_id = ""
    return user_id
