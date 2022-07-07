from pydantic import BaseSettings, Field, SecretStr


class ModelManagementSettings(BaseSettings):
    """Utility class for storing connection settings to Keycloak."""

    model_api_url: str = Field(..., env="MODEL_API_URL")
