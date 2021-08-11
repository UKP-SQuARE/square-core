from fastapi import FastAPI

from .core.config import settings
from .routers import api


def get_app():
    app = FastAPI(title="SQuARE Datastore API")

    app.include_router(api.router, prefix=settings.API_PREFIX)

    return app


app = get_app()
