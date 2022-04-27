import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration
    """

    APP_VERSION: str = "0.1.0"
    APP_NAME: str = "SQuARE Explainability API"
    API_PREFIX: str = "/api"
    OPENAPI_URL: str = "/api/openapi.json"
    # set this ENV variable to `host.docker.internal` for Mac
    API_URL = os.getenv("DOCKER_HOST_URL", "https://square.ukp-lab.de")  # change later


settings = Settings()
