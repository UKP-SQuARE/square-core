
class TestQuery:
    def test_search_bm25(self, client, bm25_index, query_document):
        response = client.get("/datastores/wiki/indices/{}/search".format(bm25_index.name), params={"query": "quack"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == query_document.id

    def test_score(self, client, bm25_index, query_document):
        response = client.get("/datastores/wiki/indices/{}/score".format(bm25_index.name), params={"query": "quack"})
        assert response.status_code == 200
        assert response.json()["score"] > 0
