import pytest
from app.core.db import DatastoreDB
from app.core.generate_package import PackageGenerator
from app.models.index import IndexRequest, IndexResponse
from pytest_mock import MockerFixture

from .utils import async_return


class TestIndices:
    def test_get_indices(self, mocker: MockerFixture, client, bm25_index, dpr_index):
        mocker.patch.object(DatastoreDB, "get_indices", return_value=async_return([bm25_index, dpr_index]))

        response = client.get("/datastores/wiki/indices")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert IndexResponse.from_index(bm25_index).dict() in response.json()
        assert IndexResponse.from_index(dpr_index).dict() in response.json()

    def test_get_index(self, mocker: MockerFixture, client, dpr_index):
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(dpr_index))

        response = client.get("/datastores/wiki/indices/{}".format(dpr_index.name))
        assert response.status_code == 200
        assert response.json() == IndexResponse.from_index(dpr_index).dict()

    def test_get_index_not_found(self, mocker: MockerFixture, client):
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(None))

        response = client.get("/datastores/wiki/indices/not_found")
        assert response.status_code == 404

    # TODO API method not implemented yet
    @pytest.mark.skip
    def test_get_index_status(self, mocker: MockerFixture, client, dpr_index):
        response = client.get("/datastores/wiki/indices/{}/status".format(dpr_index.name))
        assert response.status_code == 200

    def test_put_index(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(None))
        mocker.patch.object(DatastoreDB, "add_index", return_value=async_return(True))
        mocker.patch.object(DatastoreDB, "update_index", return_value=async_return(True))
        mocker.patch.object(DatastoreDB, "add_query_type_field", return_value=async_return(True))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        index_name = "test_index"
        index = IndexRequest(bm25=True)
        response = client.put("/datastores/wiki/indices/{}".format(index_name), json=index.dict())
        assert response.status_code == 201
        assert response.json()["name"] == index_name
        assert response.json()["bm25"] is True

    def test_delete_index(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "delete_index", return_value=async_return(True))
        mocker.patch.object(DatastoreDB, "delete_query_type_field", return_value=async_return(True))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        index_name = "index_for_delete"
        response = client.delete("/datastores/wiki/indices/{}".format(index_name))
        assert response.status_code == 204

    def test_delete_index_not_found(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "delete_index", return_value=async_return(False))
        mocker.patch.object(DatastoreDB, "delete_query_type_field", return_value=async_return(False))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        response = client.delete("/datastores/wiki/indices/not_found")
        assert response.status_code == 404
