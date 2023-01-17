import os
from typing import Tuple, Iterable, List
from fastapi.testclient import TestClient

import pytest
from app.core.es.connector import ElasticsearchConnector
from app.core.kgs.connector import KnowledgeGraphConnector
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
    get_kg_storage_connector,
)
import jwt

for k, v in settings.dict().items():
    os.environ[k] = str(v)  # have to set up the ENV before importing MongoDbContainer
import asyncio
from tests.utils import get_container_ip, start_container, wait_for_up, inside_container

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
def bing_search_datastore_name():
    return "bing_search"

@pytest.fixture(scope="package")
def bing_search_datastore(bing_search_datastore_name):
    return Datastore(
        name=bing_search_datastore_name,
        fields=[
            DatastoreField(name="text", type="text"),
            DatastoreField(name="title", type="text"),
        ],
    )

# Wikidata-KG test preparations
@pytest.fixture(scope="package")
def wikidata_kg_name():
    return "wikidata"

@pytest.fixture(scope="package")
def wikidata_kg(wikidata_kg_name):
    return Datastore(
        name=wikidata_kg_name,
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
def es_container(
    wiki_datastore: Datastore,
    wikidata_kg: Datastore,
    bing_search_datastore: Datastore,
    mongo_container: Tuple[str, str],
    user_id: str,
    dpr_index: Index,
    second_index: Index,
    test_document: Document,
    query_document: Document,
) -> str:
    # TODO: Use real docker via testcontainers
    # os.environ["TC_HOST"] = settings.ES_URL
    # es = ElasticSearchContainer(image="elasticsearch:7.16.1", remove=True, mem_limit="512m")
    # import ipdb; ipdb.set_trace()
    # es.start()
    es_container = start_container(
        image="elasticsearch:7.16.1",
        port_host=9200,
        port_container=9200,
        network=None,
        name="es",
        mem_limit="10g",
    )
    es_container.start()
    host_ip = get_container_ip("es")
    # print(f"ip of es :{host_ip}")
    # host_ip = "localhost"
    host_url = f"http://{host_ip}:9200"
    wait_for_up(host_url)
    try:
        es_connector = ElasticsearchConnector(host_url)
        kg_connector = KnowledgeGraphConnector(host_url)
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(es_connector.add_datastore(wiki_datastore)),
            loop.create_task(es_connector.add_datastore(bing_search_datastore)),
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
            loop.create_task(kg_connector.add_kg(wikidata_kg)),
        ]
        loop.run_until_complete(asyncio.gather(*tasks))

        # Add bindings for wiki datastore, bing search, wikidata:
        datastore_names = [wiki_datastore.name, bing_search_datastore.name, wikidata_kg.name]
        for datastore_name in datastore_names:
            mongo_client = build_mongo_client(*mongo_container)
            mongo_client.user_datastore_bindings.insert_one(
                {
                    "user_id": user_id,
                    mongo_client.item_keys["datastore"]: datastore_name,
                }
            )
            
        yield host_url
    finally:
        es_container.stop()


@pytest.fixture(scope="function")
def es_connector(es_container: str):
    return ElasticsearchConnector(es_container)


@pytest.fixture(scope="function")
def mock_search_client(es_connector):
    model_api = ModelAPIClient(settings.MODEL_API_URL)
    faiss = FaissClient()
    return DenseRetrieval(es_connector, model_api, faiss)


@pytest.fixture(scope="package")
def mongo_container() -> Tuple[str, str]:
    mongo_container = start_container(
        image="mongo:latest",
        port_host=27017,
        port_container=27017,
        network=None,
        name="mongo",
        envs={
            "MONGO_INITDB_ROOT_USERNAME": "test",
            "MONGO_INITDB_ROOT_PASSWORD": "test",
        },
    )
    mongo_container.start()
    host_ip = get_container_ip("mongo")
    host_url = f"http://{host_ip}"
    port = 27017
    wait_for_up(f"{host_url}:{port}")
    try:
        yield (f"mongodb://test:test@{host_ip}", port)
    finally:
        mongo_container.stop()


def build_mongo_client(host_ip: str, port: str) -> MongoClient:
    return MongoClient(
        host_ip,  # Inside docker, we cannot use localhost
        port,
        settings.MONGO_INITDB_ROOT_USERNAME,
        settings.MONGO_INITDB_ROOT_PASSWORD,
        settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
    )


@pytest.fixture(scope="function")
def mongo_client(mongo_container) -> MongoClient:
    host_ip, port = mongo_container
    return build_mongo_client(host_ip, port)


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def client(es_container, mock_search_client, mongo_client, token) -> TestClient:
    app = get_app()
    app.dependency_overrides[auth] = lambda: token
    app.dependency_overrides[client_credentials] = lambda: token
    app.dependency_overrides[get_storage_connector] = lambda: ElasticsearchConnector(
        es_container
    )
    app.dependency_overrides[get_kg_storage_connector] = lambda: KnowledgeGraphConnector(
        es_container
    )
    app.dependency_overrides[get_search_client] = lambda: mock_search_client
    app.dependency_overrides[get_mongo_client] = lambda: mongo_client
    client = TestClient(app)
    return client
