from fastapi import FastAPI, Depends
import auth_api.security as security

app = FastAPI()

@app.get("/auth")
async def auth(authenticated: bool = Depends(security.validate_request),):
    return {"authenticated": True}
