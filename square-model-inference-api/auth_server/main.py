from fastapi import FastAPI, Depends
import auth_api.security as security
from logging.config import fileConfig
import logging

logger = logging.getLogger(__name__)
try:
    fileConfig("logging.conf", disable_existing_loggers=False)
except:
    logger.info("Failed to load 'logging.conf'. Continuing without configuring the server logger")
app = FastAPI()


@app.get("/auth")
async def auth(authenticated: bool = Depends(security.validate_request)):
    # authenticated is always True because security.validate_request raises an exception if validation fails
    # and it does not return False
    return {"authenticated": authenticated}
