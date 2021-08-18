import pytest
from app.models.index import IndexRequest, IndexResponse
from requests_mock import Mocker


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

    # TODO API method not implemented yet
    @pytest.mark.skip
    def test_get_index_status(self, client, dpr_index):
        response = client.get("/datastores/wiki/indices/{}/status".format(dpr_index.name))
        assert response.status_code == 200

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

    def test_get_document_embedding(self, client, dpr_index, test_document, test_document_embedding):
        response = client.get(
            "/datastores/wiki/indices/{0}/embeddings/{1}".format(dpr_index.name, test_document["id"])
        )
        assert response.status_code == 200
        assert response.json()["id"] == test_document["id"]
        assert response.json()["embedding"] == test_document_embedding

    def test_set_document_embedding(self, client, dpr_index, query_document):
        embedding = [1] * 769
        response = client.post(
            "/datastores/wiki/indices/{0}/embeddings/{1}".format(dpr_index.name, query_document["id"]),
            json=embedding,
        )
        assert response.status_code == 200

    def test_upload_embeddings(self, client, dpr_index, embeddings_file):
        response = client.post(
            "/datastores/wiki/indices/{0}/embeddings/upload".format(dpr_index.name),
            files={"file": embeddings_file},
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_documents_from_urls(
        self, requests_mock: Mocker, client, dpr_index, embeddings_file, upload_urlset
    ):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], body=embeddings_file)

        response = client.post(
            "/datastores/wiki/indices/{0}/embeddings".format(dpr_index.name),
            json=upload_urlset.dict(),
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_documents_from_urls_invalid(self, requests_mock: Mocker, client, dpr_index, upload_urlset):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], status_code=404)

        response = client.post(
            "/datastores/wiki/indices/{0}/embeddings".format(dpr_index.name),
            json=upload_urlset.dict(),
        )
        assert response.status_code == 400
        assert response.json()["successful_uploads"] == 0

    # TODO add tests for downloading all embeddings
