from multiprocessing import Process
import os
import time
from fastapi import FastAPI

import pytest
import requests
from app.core.es.connector import ElasticsearchConnector
from app.core.config import settings
from app.core.dense_retrieval import DenseRetrieval
from app.core.faiss import FaissClient
from app.core.model_api import ModelAPIClient
from app.core.mongo import MongoClient
from app.main import get_app, auth
from app.models.datastore import Datastore, DatastoreField
from app.models.document import Document
from app.models.index import Index
from app.models.upload import UploadUrlSet
from app.routers.dependencies import (
    get_search_client,
    get_storage_connector,
    client_credentials,
    get_mongo_client,
)
import jwt

for k, v in settings.dict().items():
    os.environ[k] = str(v)  # have to set up the ENV before importing MongoDbContainer
from testcontainers.mongodb import MongoDbContainer
from testcontainers.elasticsearch import ElasticSearchContainer
import asyncio
import tqdm
import uvicorn


file_dir = os.path.dirname(__file__)


@pytest.fixture
def documents_file():
    f = open(file_dir + "/fixtures/0.jsonl", "rb")
    yield f
    f.close()


@pytest.fixture
def embeddings_file():
    f = open(file_dir + "/fixtures/0.hdf5", "rb")
    yield f
    f.close()


@pytest.fixture(scope="package")
def datastore_name():
    return "datastore-test-wiki"


@pytest.fixture(scope="package")
def upload_urlset():
    return UploadUrlSet(urls=["http://imaginary_url"])


@pytest.fixture(scope="package")
def wiki_datastore(datastore_name):
    return Datastore(
        name=datastore_name,
        fields=[
            DatastoreField(name="text", type="text"),
            DatastoreField(name="title", type="text"),
        ],
    )


@pytest.fixture(scope="package")
def dpr_index(datastore_name: str) -> Index:
    return Index(
        datastore_name=datastore_name,
        name="dpr",
        doc_encoder_model="facebook/dpr-ctx_encoder-single-nq-base",
        query_encoder_model="facebook/dpr-question_encoder-single-nq-base",
        embedding_size=768,
    )


@pytest.fixture(scope="package")
def second_index(datastore_name: str) -> Index:
    return Index(
        datastore_name=datastore_name,
        name="second",
        doc_encoder_model="doc_encoder_second_index",
        query_encoder_model="query_encoder_second_index",
        embedding_size=768,
    )


@pytest.fixture(scope="package")
def test_document() -> Document:
    return Document(
        __root__={
            "id": "111",
            "title": "test document",
            "text": "this is a test document",
        }
    )


@pytest.fixture(scope="package")
def test_document_embedding():
    return [0] * 769


@pytest.fixture(scope="package")
def query_document() -> Document:
    return Document(
        __root__={
            "id": "222",
            "title": "document title",
            "text": "document containing the query word quack",
        }
    )


@pytest.fixture(scope="package")
def user_id() -> str:
    return "test-user"


@pytest.fixture(scope="package")
def mock_connector(
    wiki_datastore: Datastore,
    mock_mongo_client: MongoClient,
    user_id: str,
    dpr_index: Index,
    second_index: Index,
    test_document: Document,
    query_document: Document,
):
    # TODO: Use real docker via testcontainers
    # os.environ["TC_HOST"] = settings.ES_URL
    es_container = ElasticSearchContainer("elasticsearch:7.16.1")
    es_container.start()
    host_url = es_container.get_url()

    try:
        es_connector = ElasticsearchConnector(host_url)
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(es_connector.add_datastore(wiki_datastore)),
            loop.create_task(es_connector.add_index(dpr_index)),
            loop.create_task(es_connector.add_index(second_index)),
            loop.create_task(
                es_connector.add_document(
                    wiki_datastore.name, test_document.id, test_document
                )
            ),
            loop.create_task(
                es_connector.add_document(
                    wiki_datastore.name, query_document.id, query_document
                )
            ),
        ]
        loop.run_until_complete(asyncio.gather(*tasks))
        es_connector = ElasticsearchConnector(
            host_url
        )  # otherwise: "RuntimeError: Timeout context manager should be used inside a task"

        # add binding
        datastore_name = wiki_datastore.name
        mock_mongo_client.user_datastore_bindings.insert_one(
            {
                "user_id": user_id,
                mock_mongo_client.item_keys["datastore"]: datastore_name,
            }
        )
        yield es_connector
    finally:
        es_container.stop()


@pytest.fixture(scope="package")
def mock_search_client(mock_connector):
    model_api = ModelAPIClient(settings.MODEL_API_URL)
    faiss = FaissClient()
    return DenseRetrieval(mock_connector, model_api, faiss)


@pytest.fixture(scope="package")
def mock_mongo_client():
    mongo_container = MongoDbContainer("mongo:latest")
    mongo_container.start()
    mongo_container.get_connection_client().list_databases()  # This is actually for waiting the docker to be ready
    port = mongo_container.get_exposed_port(
        settings.MONGO_PORT
    )  # We need to get this from testcontainers, since it is generated but set
    try:
        yield MongoClient(
            mongo_container.get_container_host_ip(),  # Inside docker, we cannot use localhost
            port,
            settings.MONGO_INITDB_ROOT_USERNAME,
            settings.MONGO_INITDB_ROOT_PASSWORD,
            settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        )
    finally:
        mongo_container.stop()


@pytest.fixture(scope="package")
def token(user_id):
    token = jwt.encode(
        {
            "preferred_username": user_id,
            "iss": "https://square.ukp-lab.test/auth/realms/test-realm",
        },
        "secret",
        algorithm="HS256",
    )
    return token


@pytest.fixture(scope="package")
def token_no_permission():
    token = jwt.encode(
        {
            "preferred_username": "test-user-no-permission",
            "iss": "https://square.ukp-lab.test/auth/realms/test-realm",
        },
        "secret",
        algorithm="HS256",
    )
    return token


def run_server(app: FastAPI, host: str, port: int):
    uvicorn.run(app, host=host, port=port)


@pytest.fixture(scope="package")
def client(mock_connector, mock_search_client, mock_mongo_client, token) -> str:
    app = get_app()
    app.dependency_overrides[auth] = lambda: token
    app.dependency_overrides[client_credentials] = lambda: token
    app.dependency_overrides[get_storage_connector] = lambda: mock_connector
    app.dependency_overrides[get_search_client] = lambda: mock_search_client
    app.dependency_overrides[get_mongo_client] = lambda: mock_mongo_client

    host = "0.0.0.0"
    port = 7000
    proc = Process(target=run_server, args=(app, host, port), daemon=True)
    proc.start()
    url = f"http://{host}:{port}"

    timeout = 100
    for _ in tqdm.trange(timeout, desc="Waiting for server up (s)"):
        try:
            response = requests.get(f"{url}/docs#")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    yield url
    proc.kill()
