from fastapi import FastAPI, Depends

from .core.config import settings
from .core.auth import verify_api_key
from .routers import api


def get_app():
    app = FastAPI(title="SQuARE Datastore API",
                  dependencies=[Depends(verify_api_key)],
                  openapi_url=settings.OPENAPI_URL)

    app.include_router(api.router, prefix=settings.API_PREFIX)

    return app


app = get_app()
