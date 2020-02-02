from flask import Flask
from flask_cors import CORS
from .api import api, jwt
from .models import db

def create_app(app_name="SQUARE_API"):
    app = Flask(app_name)

    app.config.from_json("config.json")

    app.register_blueprint(api, url_prefix="/api")

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    jwt.init_app(app)

    return app