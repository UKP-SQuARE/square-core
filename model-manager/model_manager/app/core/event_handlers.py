import logging
from typing import Callable

from model_manager.app.db.database import MongoClass


logger = logging.getLogger(__name__)


def _startup_model() -> None:
    """
    Connect to the db
    """
    MongoClass()


def _shutdown_model() -> None:
    """close the db connection"""
    mongo_client = MongoClass()
    mongo_client.close()


def start_app_handler() -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_model()

    return startup


def stop_app_handler() -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model()

    return shutdown
