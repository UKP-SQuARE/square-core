from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    API_PREFIX: str = ""
    OPENAPI_URL: str = "/datastores/openapi.json"
    API_KEY: SecretStr = ""
    ES_URL: str = ""
    ES_SEARCH_TIMEOUT: int = 30
    # Requests to FAISS_URL will first be received by Traefik, which will then forward to the right container.
    FAISS_URL: str = ""
    UPLOAD_BATCH_SIZE: int = 1000
    MODEL_API_URL: str = ""
    MAX_RETURN_ITEMS: int = 10000

    class Config:
        env_file = ".env"


settings = Settings()
