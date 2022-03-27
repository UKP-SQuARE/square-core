import pytest
from app.core.config import settings
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

    def test_get_index_status(self, requests_mock: Mocker, client, datastore_name, dpr_index):
        requests_mock.real_http = True
        requests_mock.get(
            f"{settings.MODEL_API_URL}/{dpr_index.query_encoder_model.replace('/', '-')}/health/heartbeat",
            json={"is_alive": True},
        )
        requests_mock.get(
            f"{settings.FAISS_URL}/{datastore_name}/{dpr_index.name}/index_list",
            json={"device": "cpu", "index list": ["samples"], "index loaded": "samples"},
        )

        response = client.get(f"/datastores/{datastore_name}/indices/{dpr_index.name}/status")
        assert response.status_code == 200
        assert response.json() == {"is_available": True}

    def test_put_index(self, client, datastore_name, token):
        index_name = "test_index"
        index = IndexRequest()
        response = client.put(
            f"/datastores/{datastore_name}/indices/{index_name}", 
            json=index.dict(),
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == index_name
        assert response.json()["doc_encoder_model"] is None

    def test_delete_index(self, client, datastore_name, token):
        index_name = "index_for_delete"
        index = IndexRequest()
        response = client.put(
            f"/datastores/{datastore_name}/indices/{index_name}", 
            json=index.dict(),
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        response = client.delete(
            f"/datastores/{datastore_name}/indices/{index_name}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    def test_delete_index_not_found(self, client, datastore_name, token):
        response = client.delete(
            f"/datastores/{datastore_name}/indices/not_found",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_get_document_embedding(
        self, requests_mock: Mocker, client, datastore_name, dpr_index, test_document, test_document_embedding
    ):
        requests_mock.real_http = True
        requests_mock.get(
            f"{settings.FAISS_URL}/{datastore_name}/{dpr_index.name}/reconstruct",
            json={"vector": test_document_embedding},  # use an impossible score to test that this return value is used
        )

        response = client.get(
            "/datastores/{0}/indices/{1}/embeddings/{2}".format(datastore_name, dpr_index.name, test_document["id"])
        )
        assert response.status_code == 200
        assert response.json()["id"] == test_document["id"]
        assert response.json()["embedding"] == test_document_embedding

    # ================== no permission ==================
    def test_delete_index_no_permission(self, client, datastore_name, token, token_no_permission):
        index_name = "index_for_delete"
        index = IndexRequest()
        response = client.put(
            f"/datastores/{datastore_name}/indices/{index_name}", 
            json=index.dict(),
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        response = client.delete(
            f"/datastores/{datastore_name}/indices/{index_name}",
            headers={"Authorization": f"Bearer {token_no_permission}"}
        )
        assert response.status_code == 403
        response = client.delete(
            f"/datastores/{datastore_name}/indices/{index_name}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204