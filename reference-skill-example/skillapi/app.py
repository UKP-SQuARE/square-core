from flask import Flask
from flask_cors import CORS
from .api import api

def create_app(app_name="SKILL_API"):
    app = Flask(app_name)

    app.config.from_json("config.json")

    app.register_blueprint(api, url_prefix="/api")

    cors = CORS(app, resources={r"/api/ping": {"origins": "*"}})

    return app