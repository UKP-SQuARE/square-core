from app.models.datastore import DatastoreField


class TestDatastores:
    def test_get_all_datastores(self, client, wiki_datastore):
        response = client.get("/datastores")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1
        # first item should be the demo datastore
        assert response.json()[0] == wiki_datastore.dict()

    def test_get_datastore(self, client, wiki_datastore):
        response = client.get("/datastores/{}".format(wiki_datastore.name))
        assert response.status_code == 200
        assert response.json() == wiki_datastore.dict()

    def test_get_datastore_not_found(self, client):
        response = client.get("/datastores/not_found")
        assert response.status_code == 404

    def test_put_datastore(self, client):
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

    def test_cannot_override_id_field(self, client):
        new_datastore_name = "new_datastore"
        new_datastore_fields = [
            DatastoreField(name="id", type="int").dict(),
            DatastoreField(name="field1", type="string").dict(),
        ]
        response = client.put("/datastores/{}".format(new_datastore_name), json=new_datastore_fields)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Cannot use reserved field 'id'."

    def test_delete_datastore(self, client):
        datastore_name = "datastore_for_delete"
        response = client.put("/datastores/{}".format(datastore_name), json=[{"name": "text", "type": "string"}])
        assert response.status_code == 201
        response = client.delete("/datastores/{}".format(datastore_name))
        assert response.status_code == 204

    def test_delete_datastore_not_found(self, client):
        response = client.delete("/datastores/not_found")
        assert response.status_code == 404
