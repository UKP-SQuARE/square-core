
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

    # TODO currently, 204 is always returned due to Vespa
    # def test_delete_document_not_found(self, client):
    #     response = client.delete("/datastores/wiki/documents/99999")
    #     assert response.status_code == 404

    # TODO Tests for uploading from url, downloading all, and error cases
