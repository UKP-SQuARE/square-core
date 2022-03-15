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


def add_prefix_to_openapi():
    global app
    if app.openapi_schema:
        return app.openapi_schema

    prefix = os.getenv("API_PREFIX", "skill-manager")
    openapi_schema = get_openapi(
        title="Skill-Manager API",
        version="0.0.1",
        description="API reference for skill-manager.",
        routes=app.routes,
    )
    replaced_keys = {}
    for api_route in openapi_schema["paths"].keys():
        api_route_prefix = api_route.split("/")
        api_route_prefix.insert(2, prefix)
        api_route_prefix = "/".join(api_route_prefix)

        logging.debug(f"replacing: {api_route} with {api_route_prefix}")
        replaced_keys[api_route] = api_route_prefix

    openapi_schema["paths"] = {
        replaced_keys[k]: v for k, v in openapi_schema["paths"].items()
    }
    return openapi_schema

app.openapi_schema = add_prefix_to_openapi()


@app.on_event("startup")
def on_startup():
    mongo_client.connect()


@app.on_event("shutdown")
def on_shutdown():
    mongo_client.close()
