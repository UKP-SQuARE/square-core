from pydantic import BaseSettings, SecretStr, Field

class Settings(BaseSettings):
    API_PREFIX: str = Field("", env="API_PREFIX")
    OPENAPI_URL: str = Field("/datastores/openapi.json", env="OPENAPI_URL")
    API_KEY: SecretStr = Field("", env="API_KEY")
    ES_URL: str = Field("", env="ES_URL")
    ES_SEARCH_TIMEOUT: int = Field(30, env="ES_SEARCH_TIMEOUT")

    FAISS_PORT: int = Field(5000, env="FAISS_PORT")
    UPLOAD_BATCH_SIZE: int = Field(1000, env="UPLOAD_BATCH_SIZE")
    MODEL_API_URL: str = Field("", env="MODEL_API_URL")
    MAX_RETURN_ITEMS: int = Field(10000, env="MAX_RETURN_ITEMS")

    # Mongo ROOT
    MONGO_INITDB_ROOT_USERNAME: str = Field("", env="MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD: str = Field("", env="MONGO_INITDB_ROOT_PASSWORD")
    MONGO_HOST: str = Field("", env="MONGO_HOST")
    MONGO_PORT: int = Field(27017, env="MONGO_PORT")
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(3000, env="MONGO_SERVER_SELECTION_TIMEOUT_MS")
    BING_KEY: str = Field("", env="BING_KEY")

    class Config:
        env_file = ".env"

settings = Settings()
