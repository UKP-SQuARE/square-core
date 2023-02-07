from fastapi.testclient import TestClient
from app.models.datastore import Datastore
from app.models.document import Document
import json

class TestKGs:
    def test_put_kg(self, client: TestClient, token: str):
        # Given:
        new_kg_name = "kg-test-new_kg"
        new_kg_url = f"/datastores/kg/{new_kg_name}"

        # When:
        response = client.put(
            new_kg_url,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Then:
        assert response.status_code == 201
        response = client.get(new_kg_url)
        assert response.status_code == 200
        assert response.json()["name"] == new_kg_name

    def test_get_all_kgs(self, client: TestClient, conceptnet_kg: Datastore):
        # Given:
        url = "/datastores/kg"
        expected_code = 200
        
        # When:
        response = client.get(url)
        
        # Then:
        assert response.status_code == expected_code
        kgs_preset = list(filter(lambda kg: kg["name"] == conceptnet_kg.name, response.json()))
        assert len(kgs_preset) == 1
        kg_preset = kgs_preset[0]
        conceptnet_kg_json = json.loads(conceptnet_kg.json())
        for field in kg_preset["fields"]:
            assert field in conceptnet_kg_json["fields"]
        for field in conceptnet_kg_json["fields"]:
            assert field in kg_preset["fields"]

    def test_get_conceptnet(self, client: TestClient, conceptnet_kg: Datastore):
        # Given:
        url = f"/datastores/kg/{conceptnet_kg.name}"
        expected_code = 200

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code
        assert sorted(response.json()['fields'], key=lambda x: x['name']) == sorted(conceptnet_kg.dict()['fields'], key=lambda x: x['name'])

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
        kg_name = "new_kg"
        url = f"/datastores/kg/{kg_name}"

        expected_code_put_kg = 201
        expected_code_get_sucess = 200
        expected_code_delete = 204
        expected_code_get_not_found = 404

        response_put_kg = client.put(
            "/datastores/kg/{}".format(kg_name),
            json=conceptnet_kg.dict()['fields'],
            headers={"Authorization": f"Bearer {token}"},
        )

        # When:
        response_get = client.get(url)
        response_delete = client.delete(url, headers={"Authorization": f"Bearer {token}"})
        response_get2 = client.get(url)

        # Then:
        assert response_put_kg.status_code == expected_code_put_kg
        assert response_get.status_code == expected_code_get_sucess     
        assert response_delete.status_code == expected_code_delete
        assert response_get2.status_code == expected_code_get_not_found
    
    def test_get_node(self, client: TestClient, kg_name: str, test_node: Document):
        # Given:
        nid = test_node['id']
        url = f"/datastores/kg/{kg_name}/{nid}"

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == 200
        assert response.json()[nid] == test_node


    def test_get_node_not_found(self, client: TestClient, kg_name: str):
        # Given:
        url = f"/datastores/kg/{kg_name}/documents/n99999999"
        expected_code = 404

        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code

    def test_put_node(self, client: TestClient, kg_name: str, token: str):
        # Given:
        node_id = "n999999"
        node =  {
            'id': node_id,
            'name': 'test_node_name',
            'type': 'node',
            'description': 'This_is_a_test_node',
            'weight': None,
            'in_id': None,
            'out_id': None,
        }
        url_put = f"/datastores/kg/{kg_name}/nodes/{node_id}"
        url_get = f"/datastores/kg/{kg_name}/{node_id}"

        # When:
        response_post = client.put(
            url_put, 
            json=node,
            headers={"Authorization": f"Bearer {token}"}
        )
        # request added document to see if it was added correctly
        response_get = client.get(url_get)

        # Then:
        assert response_post.status_code == 201
        assert response_get.status_code == 200
        assert response_get.json() == {node_id: node}

    def test_put_nodes(self, client: TestClient, kg_name: str, token: str):
        # Given:
        node_id = "n999999"
        nodes = {
            node_id: {
                'id': node_id,
                'name': 'test_node_name',
                'type': 'node',
                'description': 'This_is_a_test_node',
                'weight': None,
                'in_id': None,
                'out_id': None,
            }
        }
        url_post = f"/datastores/kg/{kg_name}/nodes/"
        url_get = f"/datastores/kg/{kg_name}/{node_id}"

        # When:
        response_post = client.post(
            url_post, 
            json=list(nodes.values()),
            headers={"Authorization": f"Bearer {token}"}
        )
        # request added document to see if it was added correctly
        response_get = client.get(url_get)

        # Then:
        assert response_post.status_code == 201
        assert response_get.status_code == 200
        assert response_get.json() == nodes