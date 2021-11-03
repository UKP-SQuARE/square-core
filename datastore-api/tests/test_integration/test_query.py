import pytest
from app.models.query import QueryResult


class TestQuery:
    @pytest.fixture
    def query_result(self, query_document):
        return QueryResult(score=0, document=query_document)

    def test_search_bm25(self, client, datastore_name, query_document, query_result):
        response = client.get(
            "/datastores/{}/search".format(datastore_name),
            params={"query": "quack"},
        )
        assert response.status_code == 200
        assert response.json()[0]["document"] == query_result.document.__root__

    def test_search_not_found(self, client, datastore_name):
        response = client.get(
            "/datastores/{}/search".format(datastore_name),
            params={"query": "quack", "index_name": "unknown_index"},
        )
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_score(self, client, datastore_name, query_document, query_result):
        response = client.get(
            "/datastores/{}/score".format(datastore_name),
            params={"query": "quack", "doc_id": query_document["id"]},
        )
        assert response.status_code == 200
        assert "document" in response.json()
        assert response.json()["document"] == query_result.document.__root__

    def test_score_not_found(self, client, datastore_name):
        response = client.get(
            "/datastores/{}/score".format(datastore_name),
            params={"query": "quack", "doc_id": 99999},
        )
        assert response.status_code == 404
        assert "detail" in response.json()
