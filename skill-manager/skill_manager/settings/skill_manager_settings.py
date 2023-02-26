from pydantic import BaseSettings, Field, SecretStr


class SkillManagerSettings(BaseSettings):
    """Utility class for storing connection settings to Keycloak."""

    model_api_url: str = Field(..., env="MODEL_API_URL")
    evaluator_api_url: str = Field(..., env="EVALUATOR_API_URL")
