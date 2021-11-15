import pytest
from app.models.index import IndexRequest
from requests_mock import Mocker


class TestIndices:
    def test_get_indices(self, client, datastore_name, dpr_index, second_index):
        response = client.get(f"/datastores/{datastore_name}/indices")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert dpr_index.dict() in response.json()
        assert second_index.dict() in response.json()

    def test_get_index(self, client, datastore_name, dpr_index):
        response = client.get(f"/datastores/{datastore_name}/indices/{dpr_index.name}")
        assert response.status_code == 200
        assert response.json() == dpr_index.dict()

    def test_get_index_not_found(self, client, datastore_name):
        response = client.get(f"/datastores/{datastore_name}/indices/not_found")
        assert response.status_code == 404

    # TODO API method not implemented yet
    @pytest.mark.skip
    def test_get_index_status(self, client, datastore_name, dpr_index):
        response = client.get(f"/datastores/{datastore_name}/indices/{dpr_index.name}/status")
        assert response.status_code == 200

    def test_put_index(self, client, datastore_name):
        index_name = "test_index"
        index = IndexRequest()
        response = client.put(f"/datastores/{datastore_name}/indices/{index_name}", json=index.dict())
        assert response.status_code == 201
        assert response.json()["name"] == index_name
        assert response.json()["doc_encoder_model"] is None

    def test_delete_index(self, client, datastore_name):
        index_name = "index_for_delete"
        index = IndexRequest()
        response = client.put(f"/datastores/{datastore_name}/indices/{index_name}", json=index.dict())
        assert response.status_code == 201
        response = client.delete(f"/datastores/{datastore_name}/indices/{index_name}")
        assert response.status_code == 204

    def test_delete_index_not_found(self, client, datastore_name):
        response = client.delete(f"/datastores/{datastore_name}/indices/not_found")
        assert response.status_code == 404

    def test_get_document_embedding(self, client, datastore_name, dpr_index, test_document, test_document_embedding):
        response = client.get(
            "/datastores/{0}/indices/{1}/embeddings/{2}".format(datastore_name, dpr_index.name, test_document["id"])
        )
        assert response.status_code == 200
        assert response.json()["id"] == test_document["id"]
        assert response.json()["embedding"] == test_document_embedding

    def test_set_document_embedding(self, client, datastore_name, dpr_index, query_document):
        embedding = [1] * 769
        response = client.post(
            "/datastores/{0}/indices/{1}/embeddings/{2}".format(datastore_name, dpr_index.name, query_document["id"]),
            json=embedding,
        )
        assert response.status_code == 200

    def test_set_document_embedding_not_found(self, client, datastore_name, dpr_index):
        embedding = [1] * 769
        response = client.post(
            "/datastores/{0}/indices/{1}/embeddings/{2}".format(datastore_name, dpr_index.name, 9999),
            json=embedding,
        )
        assert response.status_code == 404

    # TODO currently not supported
    @pytest.mark.skip
    def test_upload_embeddings(self, client, datastore_name, dpr_index, embeddings_file):
        response = client.post(
            "/datastores/{0}/indices/{1}/embeddings/upload".format(datastore_name, dpr_index.name),
            files={"file": embeddings_file},
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    # TODO currently not supported
    @pytest.mark.skip
    def test_upload_embeddings_from_urls(
        self, requests_mock: Mocker, client, datastore_name, dpr_index, embeddings_file, upload_urlset
    ):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], body=embeddings_file)

        response = client.post(
            "/datastores/{0}/indices/{1}/embeddings".format(datastore_name, dpr_index.name),
            json=upload_urlset.dict(),
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_embeddings_from_urls_invalid(self, requests_mock: Mocker, client, datastore_name, dpr_index, upload_urlset):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], status_code=404)

        response = client.post(
            "/datastores/{0}/indices/{1}/embeddings".format(datastore_name, dpr_index.name),
            json=upload_urlset.dict(),
        )
        assert response.status_code == 400
        assert response.json()["successful_uploads"] == 0

    # TODO add tests for downloading all embeddings
