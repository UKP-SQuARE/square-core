import secrets

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from .config import API_KEY, API_KEY_NAME
from .messages import AUTH_REQ, NO_API_KEY

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def validate_request(query: str = Security(api_key_query),
                     header: str = Security(api_key_header),) -> bool:
    if query is None and header is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=NO_API_KEY, headers={}
        )
    elif not secrets.compare_digest(query, str(API_KEY)) \
            or not secrets.compare_digest(header, str(API_KEY)):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=AUTH_REQ, headers={}
        )
    return True
