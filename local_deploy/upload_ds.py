import json
from typing import List
from square_auth.client_credentials import ClientCredentials
import tqdm
import requests
import os


def get_token() -> str:
    client_credentials = ClientCredentials(
        keycloak_base_url="",
        buffer=60,
    )
    return client_credentials()


def get_datastores() -> dict:
    response = requests.get(
        "http://localhost:7000/datastores",
        headers={"Authorization": f"Bearer {get_token()}"},
    )
    print(response.json())


def download_beir_and_load(dataset_name: str) -> List[dict]:
    if not os.path.exists(f"{dataset_name}.zip"):
        os.system(
            f"wget https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset_name}.zip"
        )
    if not os.path.exists(dataset_name):
        os.system(f"unzip {dataset_name}.zip")

    fpath = os.path.join(dataset_name, "corpus.jsonl")
    nlines = sum(1 for _ in open(fpath))
    docs = []
    with open(fpath, "r") as f:
        for line in tqdm.tqdm(f, total=nlines, desc="Loading documents"):
            line_dict = json.loads(line)
            docs.append(
                {
                    "id": line_dict["_id"],
                    "title": line_dict["title"],
                    "text": line_dict["text"],
                }
            )

    return docs


def create_datastore(datastore_name: str) -> None:
    print(
        "Create datastore:",
        requests.put(
            f"http://localhost:7000/datastores/{datastore_name}",
            headers={"Authorization": f"Bearer {get_token()}"},
            json=[{"name": "title", "type": "text"}, {"name": "text", "type": "text"}],
        ),
    )


def upload_documents(datastore_name: str, docs: List[dict]) -> None:
    batch_size = 500
    for b in tqdm.tqdm(range(0, len(docs), batch_size), desc="Uploading documents"):
        response = requests.post(
            f"http://localhost:7000/datastores/{datastore_name}/documents",
            headers={"Authorization": f"Bearer {get_token()}"},
            json=docs[b : b + batch_size],
        )
        assert response.status_code == 201, response.status_code


def get_all_documents(datastore_name: str):
    response = requests.get(
        f"http://localhost:7000/datastores",
        headers={"Authorization": f"Bearer {get_token()}"},
    )
    return response.json()


def get_stats(datastore_name: str) -> dict:
    response = requests.get(
        f"http://localhost:7000/datastores/{datastore_name}/stats",
        headers={"Authorization": f"Bearer {get_token()}"},
    )
    return response.json()


def search(datastore_name: str, query: str) -> dict:
    response = requests.get(
        f"http://localhost:7000/datastores/{datastore_name}/search",
        headers={"Authorization": f"Bearer {get_token()}"},
        params={"query": query, "top_k": 3},
    )
    return response.json()


if __name__ == "__main__":
    # export SQUARE_PRIVATE_KEY_FILE=${PWD}/local_deploy/private_key.pem; python local_deploy/upload_ds.py
    get_datastores()
    dataset_name = "scifact"
    docs = download_beir_and_load(dataset_name)
    create_datastore(dataset_name)
    upload_documents(dataset_name, docs)
    print("Stats:", get_stats(dataset_name))
    print(
        "Search results:\n",
        search(dataset_name, "1 in 5 million in UK have abnormal PrP positivity."),
    )
