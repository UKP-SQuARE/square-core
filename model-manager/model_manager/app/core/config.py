import os
from pydantic import BaseSettings

import configparser

# Load the configuration file
config = configparser.ConfigParser()
config.read(os.environ['APP_CONFIG_PATH'])

import logging
logging.info(f"Loaded configuration from {os.environ['APP_CONFIG_PATH']}")


class Settings(BaseSettings):
    """
    Application configuration
    """

    APP_VERSION: str = config.get("app", "version")
    APP_NAME: str = config.get("app", "name")
    API_PREFIX: str = config.get("app", "api_prefix")
    OPENAPI_URL: str = config.get("app", "openapi_url")
    # set this ENV variable to `host.docker.internal` for Mac
    API_URL: str = config.get('app', 'api_url')
    ADMIN_USER_ID: str = config.get("user", "admin_user_id")


settings = Settings()
