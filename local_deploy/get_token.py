from square_auth.client_credentials import ClientCredentials


def get_token() -> str:
    client_credentials = ClientCredentials(
        keycloak_base_url="",
        buffer=60,
    )
    return client_credentials()


if __name__ == "__main__":
    # export SQUARE_PRIVATE_KEY_FILE=${PWD}/local_deploy/private_key.pem; python local_deploy/get_token.py
    print(get_token())
