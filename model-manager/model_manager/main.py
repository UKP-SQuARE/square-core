import logging
import os
from logging.config import fileConfig

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from square_auth.auth import Auth

from model_manager.app.core.config import settings
from model_manager.app.core.event_handlers import start_app_handler, stop_app_handler
from model_manager.app.routers.api import api_router


auth = Auth(
    keycloak_base_url=os.getenv("KEYCLOAK_BASE_URL", "https://square.ukp-lab.de")
)

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    # Set logging config.
    try:
        fileConfig("logging.conf", disable_existing_loggers=False)
    except Exception:
        logger.info(
            "Failed to load 'logging.conf'. Continuing without configuring the server logger"
        )
    fast_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=settings.OPENAPI_URL,
        dependencies=[Depends(auth)],
    )

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_app.include_router(api_router, prefix=settings.API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler())
    fast_app.add_event_handler("shutdown", stop_app_handler())

    return fast_app


def custom_openapi():
    """
    change api paths as per the end-user requirements
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API reference for model management.",
        routes=app.routes,
    )
    replaced_keys = dict()
    prefix = os.getenv("API_PREFIX", "models")
    for api in openapi_schema["paths"].keys():
        api_split = list(api.split("/"))
        api_split.insert(2, prefix)
        api_mod = "/".join(api_split)
        replaced_keys[api] = api_mod

    new_openapi_paths = {
        replaced_keys[k]: v for k, v in openapi_schema["paths"].items()
    }
    openapi_schema["paths"] = new_openapi_paths
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = get_app()
app.openapi_schema = custom_openapi()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
