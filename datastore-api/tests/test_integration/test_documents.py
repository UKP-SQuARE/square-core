import json

from requests_mock import Mocker


class TestDocuments:
    def test_get_document(self, client, test_document):
        response = client.get("/datastores/wiki/documents/1")
        assert response.status_code == 200
        assert response.json() == test_document

    def test_get_document_not_found(self, client):
        response = client.get("/datastores/wiki/documents/99999")
        assert response.status_code == 404

    def test_post_document(self, client):
        document = {"title": "a new document", "text": "some content"}
        response = client.post("/datastores/wiki/documents/41", json=document)
        assert response.status_code == 201
        assert response.headers["Location"].endswith("/datastores/wiki/documents/41")
        # request added document to see if it was added correctly
        response = client.get("/datastores/wiki/documents/41")
        assert response.status_code == 200

    def test_put_document(self, client):
        document = {"title": "a new document", "text": "some content"}
        response = client.put("/datastores/wiki/documents/42", json=document)
        assert response.status_code == 200
        assert response.headers["Location"].endswith("/datastores/wiki/documents/42")
        # request added document to see if it was added correctly
        response = client.get("/datastores/wiki/documents/42")
        assert response.status_code == 200

    def test_delete_document(self, client):
        document = {"title": "a new document", "text": "some content"}
        response = client.post("/datastores/wiki/documents/88888", json=document)
        assert response.status_code == 201
        response = client.delete("/datastores/wiki/documents/88888")
        assert response.status_code == 204

    def test_delete_document_not_found(self, client):
        response = client.delete("/datastores/wiki/documents/99999")
        assert response.status_code == 404

    def test_upload_documents(self, client, documents_file):
        response = client.post("/datastores/wiki/documents/upload", files={"file": documents_file})
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_documents_from_urls(self, requests_mock: Mocker, client, documents_file, upload_urlset):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], body=documents_file)

        response = client.post("/datastores/wiki/documents", json=upload_urlset.dict())
        assert response.status_code == 201
        assert response.json()["successful_uploads"] == 10

    def test_upload_documents_from_urls_invalid(self, requests_mock: Mocker, client, upload_urlset):
        requests_mock.real_http = True
        requests_mock.get(upload_urlset.urls[0], status_code=404)

        response = client.post("/datastores/wiki/documents", json=upload_urlset.dict())
        assert response.status_code == 400
        assert response.json()["successful_uploads"] == 0

    def test_download_documents(self, client, test_document):
        response = client.get("/datastores/wiki/documents")
        assert response.status_code == 200
        for item in response.iter_lines():
            print(item)
            data = json.loads(item)
            assert "id" in data
            assert "title" in data
            assert "text" in data
