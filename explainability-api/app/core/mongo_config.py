import logging
import os

from pydantic import BaseSettings, Field, validator

logger = logging.getLogger(__name__)


class MongoSettings(BaseSettings):
    """Utility class for storing connection settings to mongoDB."""

    # set custom env vars
    username: str = Field(..., env="MONGO_INITDB_ROOT_USERNAME")
    password: str = Field(..., env="MONGO_INITDB_ROOT_PASSWORD")
    host: str = Field(..., env="MONGO_HOST")
    port: str = Field(..., env="MONGO_PORT")
    connection_url: str = None

    # for dev run
    # class Config:
    #     env_prefix = ''  # defaults to no prefix, i.e. ""
    #     env_file = '/home/rachneet/projects/ukp/square-explainability/square-core/explainability-api/.env.dev'

    @validator("connection_url")
    def build_connection_url(cls, _, values) -> str:
        """builds the connection string for connecting to mongoDB."""
        logger.info("Constructing url from {}".format(values))
        return f"mongodb://{values['username']}:{values['password']}" f"@{values['host']}:{values['port']}"
