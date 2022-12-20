import base64
from io import BytesIO
import os
import time
import numpy as np
from square_auth.client_credentials import ClientCredentials
import requests


def get_token() -> str:
    client_credentials = ClientCredentials(
        keycloak_base_url="",
        buffer=60,
    )
    return client_credentials()


def _decode_embeddings(encoded_string: str):
    encoded_string = encoded_string.encode()
    arr_binary = base64.decodebytes(encoded_string)
    arr = np.load(BytesIO(arr_binary))
    return arr


def encode_query() -> None:
    response = requests.post(
        # "https://host.docker.internal/api/main/msmarco-distilbert-base-tas-b/embedding",
        # "http://localhost/api/main/msmarco-distilbert-base-tas-b/embedding",
        "http://traefik/api/main/msmarco-distilbert-base-tas-b/embedding",
        json={
            "input": ["1 in 5 million in UK have abnormal PrP positivity."],
            "adapter_name": None,
            "task_kwargs": {"embedding_mode": "cls"},
        },
        headers={"Authorization": f"Bearer {get_token()}"},
        verify=False,
        allow_redirects=True
    )
    print(response)
    print(response.json())

    time.sleep(2)
    task_id = response.json()["task_id"]
    response = requests.get(
        # f"https://host.docker.internal/api/main/task_result/{task_id}",
        # f"http://localhost/api/main/task_result/{task_id}",
        f"http://traefik/api/main/task_result/{task_id}",
        headers={"Authorization": f"Bearer {get_token()}"},
        verify=False,
    )
    print(response)
    print(response.json())
    emb = _decode_embeddings(response.json()["result"]["model_outputs"]["embeddings"])
    print(emb)


if __name__ == "__main__":
    # export SQUARE_PRIVATE_KEY_FILE=${PWD}/local_deploy/private_key.pem; python local_deploy/encode_query.py
    os.environ["SQUARE_PRIVATE_KEY_FILE"] = os.path.join(os.getcwd(), "private_key.pem")
    encode_query()
