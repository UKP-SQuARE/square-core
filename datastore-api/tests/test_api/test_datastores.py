from app.core.db import DatastoreDB
from app.core.generate_package import PackageGenerator
from app.models.datastore import DatastoreField
from pytest_mock import MockerFixture

from .utils import async_return


class TestDatastores:
    def test_get_all_datastores(self, mocker: MockerFixture, client, wiki_schema, wiki_datastore):
        mocker.patch.object(DatastoreDB, "get_schemas", return_value=async_return([wiki_schema]))

        response = client.get("/datastores")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1
        # first item should be the demo datastore
        assert response.json()[0] == wiki_datastore.dict()

    def test_get_datastore(self, mocker: MockerFixture, client, wiki_schema, wiki_datastore):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))

        response = client.get("/datastores/{}".format(wiki_datastore.name))
        assert response.status_code == 200
        assert response.json() == wiki_datastore.dict()

    def test_get_datastore_not_found(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(None))

        response = client.get("/datastores/not_found")
        assert response.status_code == 404

    def test_put_datastore(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(None))
        mocker.patch.object(DatastoreDB, "add_schema", return_value=async_return(True))
        mocker.patch.object(DatastoreDB, "update_schema", return_value=async_return(True))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        new_datastore_name = "new_datastore"
        new_datastore_fields = [
            DatastoreField(name="field1", type="string").dict(),
            DatastoreField(name="field2", type="int").dict(),
        ]
        # this field is automatically added and thus not part of the request
        id_field = DatastoreField(name="id", type="long", use_for_ranking=False).dict()
        response = client.put("/datastores/{}".format(new_datastore_name), json=new_datastore_fields)
        assert response.status_code == 201
        assert response.json()["name"] == new_datastore_name
        assert response.json()["fields"] == [id_field] + new_datastore_fields
        assert "fieldsets" not in response.json()

    def test_cannot_override_id_field(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "add_schema", return_value=async_return(True))
        mocker.patch.object(DatastoreDB, "update_schema", return_value=async_return(True))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        new_datastore_name = "new_datastore"
        new_datastore_fields = [
            DatastoreField(name="id", type="int").dict(),
            DatastoreField(name="field1", type="string").dict(),
        ]
        response = client.put("/datastores/{}".format(new_datastore_name), json=new_datastore_fields)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Cannot use reserved field 'id'."

    def test_delete_datastore(self, mocker: MockerFixture, client, wiki_datastore):
        mocker.patch.object(DatastoreDB, "delete_schema", return_value=async_return(True))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        response = client.delete("/datastores/{}".format(wiki_datastore.name))
        assert response.status_code == 204

    def test_delete_datastore_not_found(self, mocker: MockerFixture, client):
        mocker.patch.object(DatastoreDB, "delete_schema", return_value=async_return(False))
        mocker.patch.object(PackageGenerator, "generate_and_upload", return_value=async_return(True))

        response = client.delete("/datastores/not_found")
        assert response.status_code == 404
