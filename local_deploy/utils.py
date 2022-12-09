"""Utils, e.g. build token and some shared variables."""

import os
from square_auth.utils import generate_token


def build_token() -> str:
    os.environ["SQUARE_PRIVATE_KEY_FILE"] = os.path.join(os.getcwd(), "private_key.pem")
    return generate_token()


def within_container() -> bool:
    return os.path.exists("/.dockerenv")


class SharedVariables:

    token: str = build_token()
    datastore_url: str = "http://localhost:7000"
    model_url: str = (
        "https://traefik/api" if within_container() else "https://localhost/api"
    )
