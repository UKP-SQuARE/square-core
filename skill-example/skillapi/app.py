from flask import Flask
from .api import api

def create_app(app_name="SQUARE_API"):
    app = Flask(app_name)

    app.config.from_json("config.json")

    app.register_blueprint(api, url_prefix="/api")

    return app