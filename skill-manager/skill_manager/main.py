import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from skill_manager import mongo_client
from skill_manager.routers.api import router

logger = logging.getLogger(__name__)

app = FastAPI(title="Skill-Manager API", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router, prefix="/api")

# add API_PREFIX to routes in openapi.json
prefix = os.getenv("API_PREFIX", "skill-manager")
openapi_schema = get_openapi(
    title="Skill-Manager API",
    version="0.0.1",
    description="API reference for skill-manager.",
    routes=app.routes,
)
openapi_schema["paths"] = {
    "/".join(k.split("/").insert(2, prefix)): v for k, v in openapi_schema["paths"]
}
app.openapi_schema = openapi_schema


@app.on_event("startup")
def on_startup():
    mongo_client.connect()


@app.on_event("shutdown")
def on_shutdown():
    mongo_client.close()
