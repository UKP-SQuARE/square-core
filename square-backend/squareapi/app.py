import logging
import logging.config
import yaml
from flask import Flask
from flask_cors import CORS
from .api import api, jwt, swagger, skillSelector
from .models import init_db, db
from .websocket import socketio, init_socket

logger = logging.getLogger(__name__)


def create_app(app_name="SQUARE_API", config_path="./config.yaml", logging_config_path="./logging_config.yaml"):
    logging.config.dictConfig(yaml.load(open(logging_config_path)))

    logger.info("Creating Flask App")
    config = yaml.load(open(config_path))
    app = Flask(app_name)
    app.config.from_mapping(config)

    app.register_blueprint(api, url_prefix="/api")

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(config["SQLALCHEMY_DATABASE_URI"])

    jwt.init_app(app)

    swagger.init_app(app)

    skillSelector.init_from_config(config)

    socketio.init_app(app)

    init_socket(skillSelector, swagger)
    logger.info("Successfully created the Flask App")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return socketio, app
