import logging
import logging.config
from fastapi import FastAPI
import yaml
from .api import api, model_manager
from .models import init_db

logger = logging.getLogger(__name__)


def create_app(config_path="./config.yaml", logging_config_path="./logging_config.yaml"):
    logging.config.dictConfig(yaml.load(open(logging_config_path)))
    logger.info("Creating App")
    config = yaml.load(open(config_path))
    app = FastAPI()
    app.include_router(api, prefix="/api")
    init_db(config["SQLALCHEMY_DATABASE_URI"])
    model_manager.init(config)
    logger.info("Successfully created App")
    return app