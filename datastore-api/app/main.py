from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
# from .core.auth import verify_api_key  # deprecated
from .routers import api

from square_auth.auth import Auth
auth = Auth()

def get_app():
    app = FastAPI(title="SQuARE Datastore API",
                  dependencies=[Depends(auth)],
                  openapi_url=settings.OPENAPI_URL)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api.router, prefix=settings.API_PREFIX)

    return app


app = get_app()
