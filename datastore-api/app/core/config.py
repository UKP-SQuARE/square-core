from pydantic import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = ""
    VESPA_CONFIG_URL: str
    VESPA_APP_URL: str
    VESPA_APP_EXPORT_PATH: str = ".vespa_application_config"
    # VESPA_FEED_BATCH_SIZE: int = 50
    VESPA_FEED_BATCH_SIZE: int = 10000
    MONGODB_URL: str
    MODEL_API_URL: str = ""
    MAX_RETURN_ITEMS: int = 1000

    class Config:
        env_file = ".env"


settings = Settings()
