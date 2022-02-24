import logging
from logging.config import fileConfig

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.api import api_router


# from square_auth.auth import Auth
# from square_auth.client_credentials import ClientCredentials
# auth = Auth()
# client_credentials = ClientCredentials()

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    # Set logging config.
    try:
        fileConfig("logging.conf", disable_existing_loggers=False)
    except:
        logger.info("Failed to load 'logging.conf'. Continuing without configuring the server logger")
    fast_app = FastAPI(title=settings.APP_NAME,
                       version=settings.APP_VERSION,
                       openapi_url=settings.OPENAPI_URL,
                       # dependencies=[Depends(auth)]
                       )

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_app.include_router(api_router, prefix=settings.API_PREFIX)

    return fast_app


app = get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
