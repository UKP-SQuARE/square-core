import sys

from fastapi import FastAPI
from square_model_inference.api.routes.router import api_router
from square_model_inference.core.config import API_PREFIX, APP_NAME, APP_VERSION
from square_model_inference.core.event_handlers import start_app_handler, stop_app_handler
from logging.config import fileConfig
from loguru import logger

def get_app() -> FastAPI:
    # Set logging config. Loguru uses this then, too
    try:
        fileConfig("logging.conf")
    except:
        logger.info("Failed to load 'logging.conf'. Continuing without configuring the server logger")
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION)
    fast_app.include_router(api_router, prefix=API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app

app = get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
