import json
from requests_mock import Mocker


class TestDocuments:
    def test_get_document(self, client, datastore_name, test_document):
        response = client.get(f"/datastores/{datastore_name}/documents/111")
        assert response.status_code == 200
        assert response.json() == test_document

    def test_get_document_not_found(self, client, datastore_name):
        response = client.get(f"/datastores/{datastore_name}/documents/99999")
        assert response.status_code == 404

    def test_put_document(self, client, datastore_name, token):
        # TODO: first create the datastore
        document = {"id": "42", "title": "a new document", "text": "some content"}
        response = client.put(
            f"/datastores/{datastore_name}/documents/42",
            json=document,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.headers["Location"].endswith(
            f"/datastores/{datastore_name}/documents/42"
        )
        # request added document to see if it was added correctly
        response = client.get(f"/datastores/{datastore_name}/documents/42")
        assert response.status_code == 200

    def test_put_document_invalid(self, client, datastore_name):
        document = {"title": "a new document", "text": "some content"}
        response = client.put(
            f"/datastores/{datastore_name}/documents/42", json=document
        )
        assert response.status_code in [400, 422]  # 422 for invalid ID formats

    def test_delete_document(self, client, datastore_name, token):
        document = {"id": "88888", "title": "a new document", "text": "some content"}
        response = client.put(
            f"/datastores/{datastore_name}/documents/88888",
            json=document,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        response = client.delete(
            f"/datastores/{datastore_name}/documents/88888",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

    def test_delete_document_not_found(self, client, datastore_name, token):
        response = client.delete(
            f"/datastores/{datastore_name}/documents/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_post_documents(self, client, datastore_name, token):
        document = [
            {"id": "41", "title": "a new document", "text": "some content"},
            {"id": "4141", "title": "another new document", "text": "some content"},
        ]
        response = client.post(
            f"/datastores/{datastore_name}/documents",
            json=document,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 2
        # request added document to see if it was added correctly
        response = client.get(f"/datastores/{datastore_name}/documents/41")
        assert response.status_code == 200
        response = client.get(f"/datastores/{datastore_name}/documents/4141")
        assert response.status_code == 200

    def test_post_documents_one_invalid(self, client, datastore_name):
        document = [
            {"id": "414141", "title": "a new document", "text": "some content"},
            {
                "_wrong_id": "41414141",
                "title": "another new document",
                "text": "some content",
            },
        ]
        response = client.post(f"/datastores/{datastore_name}/documents", json=document)
        assert response.status_code in [400, 422]

    def test_post_documents_invalid_datastore(self, client):
        document = [
            {"id": "41", "title": "a new document", "text": "some content"},
            {"id": "4141", "title": "another new document", "text": "some content"},
        ]
        response = client.post(
            "/datastores/datastore-test-invalid_datastore_name/documents", json=document
        )
        assert response.status_code == 404

    def test_upload_documents_from_file(
        self, client, datastore_name, documents_file, token
    ):
        response = client.post(
            f"/datastores/{datastore_name}/documents/upload",
            files={"file": documents_file},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_documents_from_urls(
        self,
        requests_mock: Mocker,
        client,
        datastore_name,
        documents_file,
        upload_urlset,
        token,
    ):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], body=documents_file)

        response = client.post(
            f"/datastores/{datastore_name}/documents/from_urls",
            json=upload_urlset.dict(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_documents_from_urls_invalid(
        self, requests_mock: Mocker, client, datastore_name, upload_urlset, token
    ):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], status_code=404)

        response = client.post(
            f"/datastores/{datastore_name}/documents/from_urls",
            json=upload_urlset.dict(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert response.json()["successful_uploads"] == 0

    def test_download_documents(self, client, datastore_name, test_document):
        response = client.get(f"/datastores/{datastore_name}/documents")
        assert response.status_code == 200
        for item in response.iter_lines():
            print(item)
            data = json.loads(item)
            assert "id" in data
            assert "title" in data
            assert "text" in data

    # ================== no permission ==================
    def test_delete_document_no_permission(
        self, client, datastore_name, token, token_no_permission
    ):
        document = {"id": "88888", "title": "a new document", "text": "some content"}
        response = client.put(
            f"/datastores/{datastore_name}/documents/88888",
            json=document,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        response = client.delete(
            f"/datastores/{datastore_name}/documents/88888",
            headers={"Authorization": f"Bearer {token_no_permission}"},
        )
        assert response.status_code == 403
    def test_unsupported_operation_for_bing_search(self, client, bing_search_datastore_name):
        response = client.get(
            f"/datastores/{bing_search_datastore_name}/documents"
        )
        assert response.status_code == 404