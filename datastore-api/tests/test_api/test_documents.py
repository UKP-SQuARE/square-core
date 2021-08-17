from app.core.db import DatastoreDB
from pytest_mock import MockerFixture
from vespa.application import Vespa, VespaResponse

from .utils import async_return


class TestDocuments:
    def test_get_document(self, mocker: MockerFixture, client, wiki_schema, test_document):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        response = VespaResponse({'pathId': '/document/v1/wiki/wiki/docid/1', 'id': 'id:wiki:wiki::1', 'fields': {'text': 'this is a test document', 'title': 'test document', 'id': 1}}, 200, "", "")
        mocker.patch.object(Vespa, "get_data", return_value=response)

        response = client.get("/datastores/wiki/documents/1")
        assert response.status_code == 200
        assert response.json() == test_document

    def test_get_document_not_found(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        response = VespaResponse({'pathId': '/document/v1/wiki/wiki/docid/99999', 'id': 'id:wiki:wiki::99999'}, 404, "", "")
        mocker.patch.object(Vespa, "get_data", return_value=response)

        response = client.get("/datastores/wiki/documents/99999")
        assert response.status_code == 404

    def test_post_document(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        response = VespaResponse({'pathId': '/document/v1/wiki/wiki/docid/41', 'id': 'id:wiki:wiki::41'}, 200, "", "")
        mocker.patch.object(Vespa, "feed_data_point", return_value=response)

        document = {"title": "a new document", "text": "some content"}
        response = client.post("/datastores/wiki/documents/41", json=document)
        assert response.status_code == 201
        assert response.headers["Location"].endswith("/datastores/wiki/documents/41")

    def test_put_document(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        response = VespaResponse({'pathId': '/document/v1/wiki/wiki/docid/42', 'id': 'id:wiki:wiki::42'}, 200, "", "")
        mocker.patch.object(Vespa, "update_data", return_value=response)

        document = {"title": "a new document", "text": "some content"}
        response = client.put("/datastores/wiki/documents/42", json=document)
        assert response.status_code == 200
        assert response.headers["Location"].endswith("/datastores/wiki/documents/42")

    def test_delete_document(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        response = VespaResponse({'pathId': '/document/v1/wiki/wiki/docid/88888', 'id': 'id:wiki:wiki::88888'}, 200, "", "")
        mocker.patch.object(Vespa, "delete_data", return_value=response)

        response = client.delete("/datastores/wiki/documents/88888")
        assert response.status_code == 204

    # TODO Tests for uploading from url, downloading all, and error cases
