from fastapi import FastAPI, Depends
import auth_api.security as security
from logging.config import fileConfig

fileConfig("logging.conf")

app = FastAPI()


@app.get("/auth")
async def auth(authenticated: bool = Depends(security.validate_request)):
    # authenticated is always True because security.validate_request raises an exception if validation fails
    # and it does not return False
    return {"authenticated": authenticated}
