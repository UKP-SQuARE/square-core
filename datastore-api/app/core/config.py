from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    API_PREFIX: str = ""
    API_KEY: SecretStr
    ES_URL: str
    FAISS_URL: str
    VESPA_FEED_BATCH_SIZE: int = 1000
    MODEL_API_URL: str = ""
    MODEL_API_KEY: str = ""
    MAX_RETURN_ITEMS: int = 10000

    class Config:
        env_file = ".env"


settings = Settings()
