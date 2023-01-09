import os
from pydantic import BaseSettings


def within_container() -> bool:
    return os.path.exists("/.dockerenv")


class Settings(BaseSettings):
    datastore_url: str = "http://localhost:7000"
    model_url_host: str = "https://localhost/api"
    model_url_container: str = "https://traefik/api"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")


settings = Settings()
os.environ["SQUARE_PRIVATE_KEY_FILE"] = os.path.join(
    os.path.dirname(__file__), "private_key.pem"
)
os.environ["SQUARE_API_URL"] = (
    settings.model_url_container if within_container() else settings.model_url_host
)
