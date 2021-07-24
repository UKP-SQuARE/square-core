from pydantic import BaseSettings


class Settings(BaseSettings):
    VESPA_CONFIG_URL: str
    VESPA_APP_URL: str
    MONGODB_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
