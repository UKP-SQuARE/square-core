import os

import pytest
from app.core.auth import verify_api_key
from app.core.config import settings
from app.core.es.class_converter import ElasticsearchClassConverter
from app.main import get_app
from app.models.datastore import Datastore, DatastoreField
from app.models.index import Index
from app.models.upload import UploadUrlSet
from elasticsearch import Elasticsearch
from fastapi.testclient import TestClient


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
            DatastoreField(name="id", type="long"),
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
def db_init(datastore_name, wiki_datastore, dpr_index, second_index, test_document, query_document):
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
def client(db_init):
    app = get_app()
    app.dependency_overrides[verify_api_key] = lambda: True
    client = TestClient(app)
    return client
