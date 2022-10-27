import requests
from square_auth.client_credentials import ClientCredentials

client_credentials = ClientCredentials(
    keycloak_base_url="",
    # realm="test-realm",
    buffer=60,
)

response = requests.get(
    "http://localhost:7000/datastores",
    headers={"Authorization": f"Bearer {client_credentials()}"},
)
print(response)

# export SQUARE_PRIVATE_KEY_FILE=${PWD}/local_deploy/private_key.pem; python local_deploy/query_ds.py