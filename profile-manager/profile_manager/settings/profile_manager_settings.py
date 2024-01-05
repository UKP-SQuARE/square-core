from pydantic import BaseSettings, Field, SecretStr


class ProfileManagerSettings(BaseSettings):
    """Utility class for storing connection settings to Keycloak."""

    square_url: str = Field(..., env="SQUARE_URL")
    evauluator_api_prefix: str = Field("evaluator", env="EVALUATOR_API_PREFIX")
