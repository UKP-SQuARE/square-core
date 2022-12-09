"""
An example script to deploy a datastore including:
- uploading a corpus (SciFact), 
- doing BM25 search, 
- embedding and indexing the corpus with dense retrievers
- and doing dense retrieval.
"""

import json
import os
import shutil
import time
from typing import List
import requests
from faiss_instant.encode_and_index import run as encode_and_index
import docker
from docker.models.containers import Container
from beir.util import download_and_unzip
from utils import SharedVariables
import tqdm


def get_datastores() -> dict:
    response = requests.get(
        f"{SharedVariables.datastore_url}/datastores",
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
    )
    print(response.json())


def download_beir_and_load(dataset_name: str) -> List[dict]:
    download_and_unzip(
        url=f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset_name}.zip",
        out_dir=".",
    )
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
    response = requests.put(
        f"{SharedVariables.datastore_url}/datastores/{datastore_name}",
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
        json=[{"name": "title", "type": "text"}, {"name": "text", "type": "text"}],
    )
    assert response.status_code in [200, 201], f"Cannot create datastore: {response}"


def upload_documents(datastore_name: str, docs: List[dict]) -> None:
    batch_size = 500
    for b in tqdm.tqdm(range(0, len(docs), batch_size), desc="Uploading documents"):
        response = requests.post(
            f"{SharedVariables.datastore_url}/datastores/{datastore_name}/documents",
            headers={"Authorization": f"Bearer {SharedVariables.token}"},
            json=docs[b : b + batch_size],
        )
        assert response.status_code == 201, f"Cannot upload docs: {response}"


def get_stats(datastore_name: str) -> dict:
    response = requests.get(
        f"{SharedVariables.datastore_url}/datastores/{datastore_name}/stats",
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
    )
    assert response.status_code == 200, f"Cannot get datastore {dataset_name} stats"
    return response.json()


def bm25_search(datastore_name: str, query: str, top_k: int) -> dict:
    response = requests.get(
        f"{SharedVariables.datastore_url}/datastores/{datastore_name}/search",
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
        params={"query": query, "top_k": top_k},
    )
    assert response.status_code == 200, f"Cannot do BM25 search: {response}"
    return response.json()


def encode_and_index_corpus(
    dataset_dir: str, embeddings_and_index_dir: str, model_name_or_path: str
) -> str:
    """Embed and index the corpus. Return the path to the index and ID files."""
    # First embed the passages and build the Faiss index:
    if os.path.exists(embeddings_and_index_dir) and len(
        os.listdir(embeddings_and_index_dir)
    ):
        print(
            f"Path {embeddings_and_index_dir} exists and is not empty. Now skip embedding and indexing"
        )
    else:
        try:
            encode_and_index(
                input_file=os.path.join(dataset_dir, "corpus.jsonl"),
                output_dir=embeddings_and_index_dir,
                model_type="sbert",
                model_name_or_path=model_name_or_path,
                chunk_size=1600,
            )
        except Exception as e:
            print("Cannot embed and index the corpus")
            raise e

    # Then copy the built index and ID files to specified path:
    faiss_container_resource_dir = os.path.join(dataset_dir, "resources")
    try:
        os.makedirs(faiss_container_resource_dir, exist_ok=True)
        shutil.copy(
            os.path.join(embeddings_and_index_dir, "ann.index"),
            os.path.join(faiss_container_resource_dir, "dense.index"),
        )
        shutil.copy(
            os.path.join(embeddings_and_index_dir, "ids.txt"),
            os.path.join(faiss_container_resource_dir, "dense.txt"),
        )
    except Exception as e:
        print(
            f"Cannot copy index and ID files from {embeddings_and_index_dir} to {faiss_container_resource_dir}"
        )
        raise e

    return faiss_container_resource_dir


def start_faiss_container(
    faiss_container_name: str,
    faiss_container_resource_dir: str,
    expose_port: int,
    wait_seconds: int = 100,
):
    """Start the Faiss container and wait for it being ready."""

    # Start the container
    try:
        client = docker.from_env()
        container: Container
        for container in client.containers.list():
            if container.name == faiss_container_name:
                print(f"Found existing Faiss container {container.id}. Now restart it")
                container.remove(force=True)
                break
        container = client.containers.run(
            image="kwang2049/faiss-instant:latest",
            remove=True,
            detach=True,
            network="square-core_default",
            ports={f"{expose_port}/tcp": 5000},
            name=faiss_container_name,
            volumes=[
                f"{os.path.abspath(faiss_container_resource_dir)}:/opt/faiss-instant/resources"
            ],
        )
        container.start()
    except Exception as e:
        print("Cannot start Faiss container")
        raise e

    # Wait for being ready
    success = False
    for _ in tqdm.trange(
        wait_seconds, desc="Waiting for the Faiss container to be ready"
    ):
        try:
            container = client.containers.get(faiss_container_name)
            ip = container.attrs["NetworkSettings"]["Networks"]["square-core_default"][
                "IPAddress"
            ]
            response = requests.get(f"http://{ip}:5000/index_list")
            assert response.json()["index loaded"]
            success = True
            break
        except Exception as e:
            time.sleep(1)
    if not success:
        raise TimeoutError("Try setting longer time waiting for Faiss")


def add_index(
    datastore_name: str,
    index_name: str,
    query_encoder_name_or_path: str,
    document_encoder_name_or_path: str,
    embedding_size: int,
    embedding_mode: str,
) -> None:
    response = requests.put(
        f"{SharedVariables.datastore_url}/datastores/{datastore_name}/indices/{index_name}",
        json={
            "doc_encoder_model": document_encoder_name_or_path,
            "query_encoder_model": query_encoder_name_or_path,
            "embedding_size": embedding_size,
            "embedding_mode": embedding_mode,
            "index_url": "",
            "index_ids_url": "",
            "index_description": "",
            "collection_url": "",
        },
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
    )
    assert response.status_code in [200, 201], f"Cannot add index: {response}"


def dense_search_by_vector(
    datastore_name: str, index_name: str, query_embedding: List[float], top_k: int
) -> dict:
    response = requests.post(
        f"{SharedVariables.datastore_url}/datastores/{datastore_name}/search_by_vector",
        json={
            "index_name": index_name,
            "query_vector": query_embedding,
            "top_k": top_k,
        },
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
    )
    assert (
        response.status_code == 200
    ), f"Cannot do dense search (by vector): {response}"
    return response.json()


def dense_search(datastore_name: str, index_name: str, query: str, top_k: int) -> dict:
    response = requests.get(
        f"{SharedVariables.datastore_url}/datastores/{datastore_name}/search",
        params={
            "index_name": index_name,
            "query": query,
            "top_k": top_k,
        },
        headers={"Authorization": f"Bearer {SharedVariables.token}"},
    )
    assert response.status_code == 200, f"Cannot do dense search: {response}"
    return response.json()


if __name__ == "__main__":
    dataset_name = "scifact"
    docs = download_beir_and_load(dataset_name=dataset_name)
    create_datastore(datastore_name=dataset_name)
    upload_documents(datastore_name=dataset_name, docs=docs)
    print(f"Stats of {dataset_name}:", get_stats(datastore_name=dataset_name))

    query = "1 in 5 million in UK have abnormal PrP positivity."
    search_result = bm25_search(datastore_name=dataset_name, query=query, top_k=3)
    print(f'Search result for query "{query}":\n', json.dumps(search_result, indent=4))

    embeddings_and_index_dir = os.path.join(dataset_name, "embeddings_and_index")
    faiss_container_resource_dir = encode_and_index_corpus(
        dataset_dir=dataset_name,
        embeddings_and_index_dir=embeddings_and_index_dir,
        model_name_or_path="msmarco-distilbert-base-tas-b",
    )

    start_faiss_container(
        faiss_container_name="faiss_scifact_tasb",
        faiss_container_resource_dir=faiss_container_resource_dir,
        expose_port=5001,
    )

    index_name = "tasb"
    query_encoder = "msmarco-distilbert-base-tas-b"
    document_encoder = "msmarco-distilbert-base-tas-b"
    embedding_mode = "cls"
    embedding_size = 768
    add_index(
        datastore_name=dataset_name,
        index_name=index_name,
        query_encoder_name_or_path=query_encoder,
        document_encoder_name_or_path=document_encoder,
        embedding_size=embedding_size,
        embedding_mode=embedding_mode,
    )

    search_result = dense_search(
        datastore_name=dataset_name,
        index_name=index_name,
        query=query,
        top_k=3,
    )
    print(
        f'Dense-search result for query "{query}":\n',
        json.dumps(search_result, indent=4),
    )
