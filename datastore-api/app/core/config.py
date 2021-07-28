from pydantic import BaseSettings


class Settings(BaseSettings):
    VESPA_CONFIG_URL: str
    VESPA_APP_URL: str
    MONGODB_URL: str
    MAX_RETURN_ITEMS: int = 1000

    class Config:
        env_file = ".env"


settings = Settings()
