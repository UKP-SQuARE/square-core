from app.models.datastore import Datastore, DatastoreField
from fastapi.testclient import TestClient


class TestDatastores:
    def test_get_all_datastores(self, client: TestClient, wiki_datastore: Datastore):
        response = client.get("/datastores")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1
        # first or second item should be the demo datastore
        assert response.json()[0] == wiki_datastore.dict() or response.json()[1] == wiki_datastore.dict() 

    def test_get_datastore(self, client: TestClient, wiki_datastore: Datastore):
        response = client.get(f"/datastores/{wiki_datastore.name}")
        assert response.status_code == 200
        assert response.json() == wiki_datastore.dict()

    def test_get_datastore_not_found(self, client):
        response = client.get("/datastores/not_found")
        assert response.status_code == 404

    def test_put_datastore(self, client: TestClient, token):
        new_datastore_name = "datastore-test-new_datastore"
        new_datastore_fields = [
            DatastoreField(name="field1", type="text").dict(),
            DatastoreField(name="field2", type="long").dict(),
        ]

        response = client.put(
            "/datastores/{}".format(new_datastore_name),
            json=new_datastore_fields,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == new_datastore_name
        assert response.json()["fields"] == new_datastore_fields
        assert "fieldsets" not in response.json()

        # get new datastore to see if it was added
        response = client.get("/datastores/{}".format(new_datastore_name))
        assert response.status_code == 200
        assert response.json()["name"] == new_datastore_name

        def sort_by(d):
            return (d["name"], d["type"])

        assert sorted(response.json()["fields"], key=sort_by) == sorted(
            new_datastore_fields, key=sort_by
        )

    def test_delete_datastore(self, client, token):
        datastore_name = "datastore-test-for_delete"
        response = client.put(
            "/datastores/{}".format(datastore_name),
            json=[{"name": "text", "type": "text"}],
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        response = client.delete(
            "/datastores/{}".format(datastore_name),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204
        response = client.get("/datastores/{}".format(datastore_name))
        assert response.status_code == 404

    def test_delete_datastore_not_found(self, client, token):
        response = client.delete(
            "/datastores/not_found", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_get_datastore_stats(self, client, datastore_name):
        response = client.get("/datastores/{}/stats".format(datastore_name))
        assert response.status_code == 200
        assert "name" in response.json()
        assert "documents" in response.json()
        assert "size_in_bytes" in response.json()

    # ================== no permission ==================
    def test_delete_datastore_no_permission(self, client, token, token_no_permission):
        datastore_name = "datastore-test-for_delete"
        response = client.put(
            "/datastores/{}".format(datastore_name),
            json=[{"name": "text", "type": "text"}],
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        response = client.delete(
            "/datastores/{}".format(datastore_name),
            headers={"Authorization": f"Bearer {token_no_permission}"},
        )
        assert response.status_code == 403
        response = client.delete(
            "/datastores/{}".format(datastore_name),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204
    def test_unsupported_operation_for_bing_search(self, client, bing_search_datastore_name):
        response = client.get(
            f"/datastores/{bing_search_datastore_name}/stats",
        )
        assert response.status_code == 404
        response = client.delete(
            f"/datastores/{bing_search_datastore_name}",
        )
        assert response.status_code == 404
        

    