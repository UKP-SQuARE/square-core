from pydantic import BaseSettings, Field, validator


class RedisSettings(BaseSettings):
    """Utility class for storing connection settings to redis."""

    username: str = Field(..., env="REDIS_USER")
    password: str = Field(..., env="REDIS_PASSWORD")
    host: str = Field(..., env="REDIS_HOST")
    port: str = Field(..., env="REDIS_PORT")
    connection_url: str = None

    @validator("connection_url")
    def build_connection_url(cls, _, values) -> str:
        """builds the connection string for connecting to redis."""
        return (
            f"redis://{values['username']}:{values['password']}"
            f"@{values['host']}:{values['port']}"
        )

    # class Config:
    #     env_file = ".env"
