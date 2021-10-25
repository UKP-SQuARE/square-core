import os
from fastapi import FastAPI
from skillapi.api.routes.router import api_router
from skillapi.core.config import API_PREFIX, APP_NAME, APP_VERSION
from skillapi.core.event_handlers import start_app_handler, stop_app_handler
from logging.config import fileConfig
import logging

logger = logging.getLogger(__name__)

def get_app() -> FastAPI:
    try:
        fileConfig(os.environ.get("LOGGING_CONFIG", "logging.conf"), disable_existing_loggers=False)
    except:
        logger.info("Failed to load 'logging.conf'. Continuing without configuring the server logger")
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION)
    fast_app.include_router(api_router, prefix=API_PREFIX)

    # Nothing done here currently.
    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app

app = get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


