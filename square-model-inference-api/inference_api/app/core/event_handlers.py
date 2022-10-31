import logging
from typing import Callable

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def _startup_model(app: FastAPI) -> None:
    """
    Initialize the model used by the server and set it to the app state for global access
    """
    pass


def _shutdown_model(app: FastAPI) -> None:
    pass


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_model(app)

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)

    return shutdown
