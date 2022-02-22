from pydantic import BaseSettings, Field, SecretStr

class KeycloakSettings(BaseSettings):
    """Utility class for storing connection settings to Keycloak."""

    base_url: str = Field(..., env="KEYCLOAK_BASE_URL")
    client_id: str = Field("skill-manager", env="KEYCLOAK_SKILL_MANAGER_CLIENT_ID")
    client_secret: SecretStr = Field(..., env="KEYCLOAK_SKILL_MANAGER_CLIENT_SECRET")
