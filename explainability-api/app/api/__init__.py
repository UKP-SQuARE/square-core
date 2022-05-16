import os

from square_auth.client_credentials import ClientCredentials


client_credentials = ClientCredentials(
    keycloak_base_url=os.getenv("KEYCLOAK_BASE_URL", "https://square.ukp-lab.de"),
    realm=os.getenv("REALM", "square-testing"),
    client_id=os.getenv("CLIENT_ID", "explainability-api"),
    client_secret=os.getenv("CLIENT_SECRET", ""),
)