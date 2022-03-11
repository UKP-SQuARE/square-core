import secrets

from fastapi.security.api_key import APIKeyHeader
from .config import settings
from fastapi import Security, HTTPException, status

import logging


logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def verify_api_key(api_key_header: str = Security(api_key_header)):
    """
    Verify API key.
    """
    logger.warning("This authorization has been deprecated. Now it uses keycloak and SQuARE-Auth")

    if api_key_header is None:
        logger.info("No API key provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No API key provided.")
    elif secrets.compare_digest(api_key_header, settings.API_KEY.get_secret_value()):
        return True
    else:
        logger.info(f"Attempted access with invalid API key {api_key_header}.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication information.")
