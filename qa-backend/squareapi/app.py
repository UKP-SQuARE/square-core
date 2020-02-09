from flask import Flask
from flask_cors import CORS
from .api import api, jwt, skillSelector
from .models import db


def create_app(app_name="SQUARE_API", config_path="config.json"):
    app = Flask(app_name)
    app.config.from_json(config_path)

    app.register_blueprint(api, url_prefix="/api")

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    jwt.init_app(app)

    skillSelector.init_from_json(config_path)

    return app