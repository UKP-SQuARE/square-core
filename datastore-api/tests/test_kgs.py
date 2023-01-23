from fastapi.testclient import TestClient
from app.models.datastore import Datastore
from app.models.document import Document

class TestKGs:
    def test_get_all_kgs(self, client: TestClient, conceptnet_kg: Datastore):
        # Given:
        url = "/datastores/kg"
        expected_code = 200
        expected_all_kgs = [conceptnet_kg.dict()]
        
        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code
        assert len(response.json()) == 1
        assert response.json() == expected_all_kgs

    def test_get_conceptnet(self, client: TestClient, conceptnet_kg: Datastore):
        # Given:
        url = "/datastores/kg/conceptnet"
        expected_code = 200

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code
        assert response.json() == conceptnet_kg.dict()

    def test_get_node_by_id(self, client: TestClient, conceptnet_kg: Datastore, test_node: Document):
        # Given:
        url = f"/datastores/kg/{conceptnet_kg.name}/{test_node.id}"
        expected_code = 200

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code
        assert response.json()[test_node.id] == test_node


    def test_get_kg_not_found(self, client: TestClient):
        # Given:
        url = "/datastores/kg/not_found"
        expected_code = 404

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code

    def test_delete_kg_not_found(self, client: TestClient):
        # Given:
        url = "/datastores/kg/not_found"
        expected_code = 404

        # When:
        response = client.delete(url)

        # Then:
        assert response.status_code == expected_code

    def test_get_kg_stats(self, client: TestClient, kg_name: str):
        # Given:
        url = f"/datastores/kg/{kg_name}/stats"
        expected_code = 200

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code
        assert "name" in response.json()
        assert "documents" in response.json()
        assert "size_in_bytes" in response.json()

    def test_delete_kg(self, client: TestClient, token: str, conceptnet_kg):
        # Given:
        kg_name = "conceptnet"
        url = f"/datastores/kg/{kg_name}"

        expected_code_get_sucess = 200
        expected_code_delete = 204
        expected_code_get_not_found = 404

        # BUG: put-Request has error
        response = client.put(
            "/datastores/kg/{}".format(kg_name),
            json=conceptnet_kg.dict()['fields'],
            headers={"Authorization": f"Bearer {token}"},
        )

        # When:
        response_get = client.get(url)
        response_delete = client.delete(url, headers={"Authorization": f"Bearer {token}"})
        response_get2 = client.get(url)

        # Then:
        assert response_get.status_code == expected_code_get_sucess     
        assert response_delete.status_code == expected_code_delete
        assert response_get2.status_code == expected_code_get_not_found