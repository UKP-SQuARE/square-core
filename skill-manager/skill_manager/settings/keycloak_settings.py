from pydantic import BaseSettings, Field, SecretStr


class KeycloakSettings(BaseSettings):
    """Utility class for storing connection settings to Keycloak."""

    base_url: str = Field(..., env="KEYCLOAK_BASE_URL")
    client_id: str = Field("skill-manager", env="CLIENT_ID")
    client_secret: SecretStr = Field(..., env="CLIENT_SECRET")
