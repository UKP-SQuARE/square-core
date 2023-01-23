import ipdb
import json
from fastapi.testclient import TestClient
from app.models.document import Document


class TestKGNodes:
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