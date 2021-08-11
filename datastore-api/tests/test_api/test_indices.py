from app.models.index import IndexRequest, IndexResponse


class TestIndices:
    def test_get_indices(self, client, bm25_index, dpr_index):
        response = client.get("/datastores/wiki/indices")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert IndexResponse.from_index(bm25_index).dict() in response.json()
        assert IndexResponse.from_index(dpr_index).dict() in response.json()

    def test_get_index(self, client, dpr_index):
        response = client.get("/datastores/wiki/indices/{}".format(dpr_index.name))
        assert response.status_code == 200
        assert response.json() == IndexResponse.from_index(dpr_index).dict()

    def test_get_index_not_found(self, client):
        response = client.get("/datastores/wiki/indices/not_found")
        assert response.status_code == 404

    def test_get_index_status(self, client, dpr_index):
        response = client.get("/datastores/wiki/indices/{}/status".format(dpr_index.name))
        assert response.status_code == 200
        # TODO
        raise NotImplementedError()

    def test_put_index(self, client):
        index_name = "test_index"
        index = IndexRequest(bm25=True)
        response = client.put("/datastores/wiki/indices/{}".format(index_name), json=index.dict())
        assert response.status_code == 201
        assert response.json()["name"] == index_name
        assert response.json()["bm25"] is True

    def test_delete_index(self, client):
        index_name = "index_for_delete"
        index = IndexRequest(bm25=True)
        response = client.put("/datastores/wiki/indices/{}".format(index_name), json=index.dict())
        assert response.status_code == 201
        response = client.delete("/datastores/wiki/indices/{}".format(index_name))
        assert response.status_code == 204

    def test_delete_index_not_found(self, client):
        response = client.delete("/datastores/wiki/indices/not_found")
        assert response.status_code == 404

    # TODO add tests for embeddings
