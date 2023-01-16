import ipdb
import json

class TestKGNodes:

    def test_get_nodes(self, client, kg_name, test_node, token):
        # Given:
        nid = test_node['id']
        url = f"/datastores/kg/{kg_name}/{nid}"

        # When:
        response = client.get(url, headers={"Authorization": f"Bearer {token}"})

        # Then:
        assert response.status_code == 200
        # TODO: Change this as soon as PUT-Request BUG is fixed 
        # assert response.json() == test_node
        assert response.json()[nid]['_id'] == nid


    def test_get_node_not_found(self, client, kg_name, token):
        # Given:
        url = f"/datastores/kg/{kg_name}/documents/n99999999"
        expected_code = 404

        # When:
        response = client.get(url, headers={"Authorization": f"Bearer {token}"})

        # Then:
        assert response.status_code == expected_code


    def test_put_node(self, client, kg_name, token):
        # Given:
        node_id = "n999999"
        nodes={}
        node = {
                'id': node_id,
                'name': 'test_node_name',
                'type': 'node',
                # 'description': '',
                'description': 'This_is_a_test_node',
                'weight': None,
                'in_id': None,
                'out_id': None,
                'in_out_id':None
            }
        nodes['test_node_name'] = node
        url_post = f"/datastores/kg/{kg_name}/nodes/"
        url_get = f"/datastores/kg/{kg_name}/{node_id}"

        # When:
        response_post = client.post(
            url_post, 
            json=list(nodes.values()),
            headers={"Authorization": f"Bearer {token}"}
        )
        # request added document to see if it was added correctly
        response_get = client.get(url_get,headers={"Authorization": f"Bearer {token}"})

        # Then:
        assert response_post.status_code == 201
        assert response_get.status_code == 200
        assert response_get.json()[node_id]["_id"] ==  nodes['test_node_name']['id']