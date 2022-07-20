from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    API_PREFIX: str = ""
    OPENAPI_URL: str = "/datastores/openapi.json"
    API_KEY: SecretStr = ""
    ES_URL: str = ""
    ES_SEARCH_TIMEOUT: int = 30

    FAISS_PORT: int = 5000
    UPLOAD_BATCH_SIZE: int = 1000
    MODEL_API_URL: str = ""
    MAX_RETURN_ITEMS: int = 10000

    # Mongo ROOT
    MONGO_INITDB_ROOT_USERNAME: str = ""
    MONGO_INITDB_ROOT_PASSWORD: str = ""
    MONGO_HOST: str = ""
    MONGO_PORT: int = 27017
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 3000

    class Config:
        env_file = ".env"


settings = Settings()
