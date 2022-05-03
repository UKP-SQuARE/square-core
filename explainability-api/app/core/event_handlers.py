import logging
from typing import Callable

from app.db.mongo_operations import Database


logger = logging.getLogger(__name__)


def _startup_model() -> None:
    """
    Connect to the db
    """
    logger.info("Initialize database")
    Database()


def _shutdown_model() -> None:
    """close the db connection"""
    mongo_client = Database()
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
