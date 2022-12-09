"""Utils, e.g. build token and some shared variables."""

import os
from square_auth.client_credentials import ClientCredentials


def build_token() -> str:
    os.environ["SQUARE_PRIVATE_KEY_FILE"] = os.path.join(os.getcwd(), "private_key.pem")
    client_credentials = ClientCredentials(
        keycloak_base_url="",
        buffer=60,
    )
    return client_credentials()


def within_container() -> bool:
    return os.path.exists("/.dockerenv")


class SharedVariables:

    token: str = build_token()
    datastore_url: str = "http://localhost:7000"
    model_url: str = (
        "https://traefik/api" if within_container() else "https://localhost/api"
    )
