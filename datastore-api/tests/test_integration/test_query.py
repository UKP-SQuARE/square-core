import pytest
from app.models.query import QueryResult, QueryResultDocument


class TestQuery:
    @pytest.fixture
    def query_result(self, query_document):
        return QueryResult(
            coverage=100,
            covered_documents=2,
            documents=[QueryResultDocument(relevance=0, document=query_document)],
        )

    def test_search_bm25(self, client, bm25_index, query_document, query_result):
        response = client.get(
            "/datastores/wiki/indices/{}/search".format(bm25_index.name),
            params={"query": "quack"},
        )
        assert response.status_code == 200
        assert response.json()["coverage"] == query_result.coverage
        assert len(response.json()["documents"]) == len(query_result.documents)
        assert response.json()["documents"][0]["document"] == query_result.documents[0].document.__root__

    def test_search_not_found(self, client):
        response = client.get(
            "/datastores/wiki/indices/unknown_index/search",
            params={"query": "quack"},
        )
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_score(self, client, bm25_index, query_document, query_result):
        response = client.get(
            "/datastores/wiki/indices/{}/score".format(bm25_index.name),
            params={"query": "quack", "doc_id": query_document["id"]},
        )
        assert response.status_code == 200
        assert "document" in response.json()
        assert response.json()["document"] == query_result.documents[0].document.__root__

    def test_score_not_found(self, client, bm25_index):
        response = client.get(
            "/datastores/wiki/indices/{}/score".format(bm25_index.name),
            params={"query": "quack", "doc_id": 99999},
        )
        assert response.status_code == 404
        assert "detail" in response.json()
