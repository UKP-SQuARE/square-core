import os

import pytest
from app.core.auth import verify_api_key
from app.core.config import settings
from app.core.dense_retrieval import DenseRetrieval
from app.core.es.class_converter import ElasticsearchClassConverter
from app.core.faiss import FaissClient
from app.core.model_api import ModelAPIClient
from app.main import get_app
from app.models.datastore import Datastore, DatastoreField
from app.models.document import Document
from app.models.index import Index
from app.models.upload import UploadUrlSet
from app.routers.dependencies import get_search_client, get_storage_connector
from elasticsearch import Elasticsearch
from fastapi.testclient import TestClient

from .utils import MockConnector


file_dir = os.path.dirname(__file__)

MOCK_DEPENDENCIES = os.environ.get("MOCK_DEPENDENCIES", "0") == "1"


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
            DatastoreField(name="id", type="long", is_id=True),
            DatastoreField(name="text", type="text"),
            DatastoreField(name="title", type="text"),
        ],
    )


@pytest.fixture(scope="package")
def dpr_index(datastore_name):
    return Index(
        datastore_name=datastore_name,
        name="dpr",
        doc_encoder_model="facebook/dpr-ctx_encoder-single-nq-base",
        query_encoder_model="facebook/dpr-question_encoder-single-nq-base",
        embedding_size=768,
    )


@pytest.fixture(scope="package")
def second_index(datastore_name):
    return Index(
        datastore_name=datastore_name,
        name="second",
        doc_encoder_model="doc_encoder_second_index",
        query_encoder_model="query_encoder_second_index",
        embedding_size=768,
    )


@pytest.fixture(scope="package")
def test_document():
    return {
        "id": 111,
        "title": "test document",
        "text": "this is a test document",
    }


@pytest.fixture(scope="package")
def test_document_embedding():
    return [0] * 769


@pytest.fixture(scope="package")
def query_document():
    return {
        "id": 222,
        "title": "document title",
        "text": "document containing the query word quack",
    }


@pytest.fixture(scope="package")
def mock_connector(wiki_datastore, dpr_index, second_index, test_document, query_document):
    return MockConnector(
        [wiki_datastore],
        [dpr_index, second_index],
        [Document(__root__=test_document), Document(__root__=query_document)],
        query_document=Document(__root__=query_document),
    )


@pytest.fixture(scope="package")
def mock_search_client(mock_connector):
    model_api = ModelAPIClient(
        settings.MODEL_API_URL
    )
    faiss = FaissClient(settings.FAISS_URL)
    return DenseRetrieval(mock_connector, model_api, faiss)


@pytest.fixture(scope="package")
def db_init(datastore_name, wiki_datastore, dpr_index, second_index, test_document, query_document):
    if MOCK_DEPENDENCIES:
        return

    converter = ElasticsearchClassConverter()
    es = Elasticsearch(hosts=[settings.ES_URL])

    # configure indices
    es.indices.delete(index="datastore-test-*")
    es.indices.create(index=datastore_name + "-docs", body=converter.convert_from_datastore(wiki_datastore))
    es.indices.create(index=datastore_name + "-search-indices", body={})
    es.index(index=datastore_name + "-search-indices", id=dpr_index.name, body=converter.convert_from_index(dpr_index))
    es.index(
        index=datastore_name + "-search-indices", id=second_index.name, body=converter.convert_from_index(second_index)
    )

    # add documents
    es.index(index=datastore_name + "-docs", id=test_document["id"], body=test_document)
    es.index(index=datastore_name + "-docs", id=query_document["id"], body=query_document)

    es.indices.refresh(index="")


@pytest.fixture(scope="package")
def client(db_init, mock_connector, mock_search_client):
    app = get_app()
    app.dependency_overrides[verify_api_key] = lambda: True
    if MOCK_DEPENDENCIES:
        app.dependency_overrides[get_storage_connector] = lambda: mock_connector
        app.dependency_overrides[get_search_client] = lambda: mock_search_client
    client = TestClient(app)
    return client
