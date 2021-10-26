from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    API_PREFIX: str = ""
    API_KEY: SecretStr
    VESPA_CONFIG_URL: str
    VESPA_APP_URL: str
    VESPA_APP_EXPORT_PATH: str = ".vespa_application_config"
    VESPA_FEED_BATCH_SIZE: int = 1000
    MONGODB_URL: str
    MODEL_API_URL: str = ""
    MODEL_API_KEY: str = ""
    MAX_RETURN_ITEMS: int = 10000

    class Config:
        env_file = ".env"


settings = Settings()
