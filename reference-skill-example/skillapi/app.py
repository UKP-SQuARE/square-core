import logging
import logging.config
import yaml
from flask import Flask
from flask_cors import CORS
from .api import api

logger = logging.getLogger(__name__)


def create_app(app_name="SQUARE_API", config_path="./config.yaml", logging_config_path="./logging_config.yaml"):
    logging.config.dictConfig(yaml.load(open(logging_config_path)))

    logger.info("Creating Flask App")
    config = yaml.load(open(config_path))
    app = Flask(app_name)
    app.config.from_mapping(config)

    app.register_blueprint(api, url_prefix="/api")

    cors = CORS(app, resources={r"/api/ping": {"origins": "*"}})
    logger.info("Successfully created Flask App")
    return app