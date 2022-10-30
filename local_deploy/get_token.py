import os
from square_auth.client_credentials import ClientCredentials


def get_token() -> str:
    client_credentials = ClientCredentials(
        keycloak_base_url="",
        buffer=60,
    )
    return client_credentials()


if __name__ == "__main__":
    os.environ["SQUARE_PRIVATE_KEY_FILE"] = os.path.join(os.getcwd(), "private_key.pem")
    print(get_token())
