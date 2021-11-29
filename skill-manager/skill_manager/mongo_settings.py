from pydantic import BaseSettings, Field, validator


class MongoSettings(BaseSettings):
    username: str = Field(..., env="MONGO_INITDB_ROOT_USERNAME")
    password: str = Field(..., env="MONGO_INITDB_ROOT_PASSWORD")
    host: str = Field(..., env="MONGO_HOST")
    port: str = Field(..., env="MONGO_PORT")
    connection_url: str = None

    @validator("connection_url")
    def build_connection_url(cls, _, values):
        return (
            f"mongodb://{values['username']}:{values['password']}"
            f"@{values['host']}:{values['port']}"
        )

    # class Config:
    #     env_file = ".env"
