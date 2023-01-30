from fastapi.testclient import TestClient
from app.models.datastore import Datastore
from app.models.document import Document
import json
from typing import Any
import ast

class TestKGs:
    def test_get_all_kgs(self, client: TestClient, conceptnet_kg: Datastore):
        # Given:
        url = "/datastores/kg"
        expected_code = 200
        
        # When:
        response = client.get(url)

        # Then:
        assert response.status_code == expected_code
        assert len(response.json()) >= 1
        assert sorted(response.json()[0]['fields'], key=lambda x: x['name']) == sorted(conceptnet_kg.dict()['fields'], key=lambda x: x['name'])

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

    def test_get_node_by_name(self, client: TestClient, conceptnet_kg: Datastore, test_node_lower: Document, token: str):
        # Given:
        url_post = f"/datastores/kg/{conceptnet_kg.name}/nodes/query_by_name"
        expected_code_post = 200
        
        nodes_upper = ["Barack_Obama"]
        nodes_lower = ["barack_obama"]

        # When:
        response_post_upper = client.post(
            url_post, 
            json=nodes_upper,
            headers={"Authorization": f"Bearer {token}"}
        )

        response_post_lower = client.post(
            url_post, 
            json=nodes_lower,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Then:
        assert response_post_lower.status_code == expected_code_post
        assert response_post_upper.status_code == expected_code_post
        assert response_post_lower.json()[test_node_lower.id] == test_node_lower
        assert response_post_upper.json()[test_node_lower.id] == test_node_lower

    def test_get_nodes_by_id(self, client: TestClient, conceptnet_kg: Datastore, test_node_lower: Document, token: str):
        # Given:
        url_post = f"/datastores/kg/{conceptnet_kg.name}/nodes/query_by_ids"
        expected_code_post = 200
        
        nodes_upper = ["n1010", "n1234"]

        # When:
        response_post = client.post(
            url_post, 
            json=nodes_upper,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Then:
        assert response_post.status_code == expected_code_post
        assert response_post.json()[test_node_lower.id] == test_node_lower

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

    #################################
    # WIKIDATA TESTS
    def test_wikidata_alive(self, client: TestClient, wikidata_kg_name: str):
        # Given:
        url = f"/datastores/kg/{wikidata_kg_name}"

        # When:
        response = client.get(url)

        # Then:
        assert response.json() == 'Wikidata API is alive'

    def test_wikidata_get_nodes_by_names(self, client: TestClient, wikidata_kg_name:str, wikidata_expected_nodes: dict):
        # Given:
        url = f"/datastores/kg/{wikidata_kg_name}/nodes/query_by_name"
        expeceted_code = 200

        # When:
        response = client.post(
            url,
            json = ["Barack Obama", "Bill Clinton"] )
        
        # Then:
        assert response.status_code == expeceted_code
        assert response.json() == wikidata_expected_nodes


    def test_wikidata_get_node_by_id(self, client: TestClient, wikidata_kg_name: str):
        # Given:
        node_id = "Q42"
        url = f"/datastores/kg/{wikidata_kg_name}/{node_id}"

        # When:
        response = client.get(url)

        # Then:
        assert response.json()[node_id]["id"] == node_id
        assert response.json()[node_id]["name"] == "Douglas Adams"
        

    def test_wikidata_get_nodes_by_ids(self, client: TestClient, wikidata_kg_name: str):
        # Given:
        node_ids = ["Q42", "Q43", "Q24"]
        url = f"/datastores/kg/{wikidata_kg_name}/nodes/query_by_ids"

        # When:
        response = client.post(url, json= node_ids)

        # Then:
        # Check keys
        assert sorted(response.json().keys()) == sorted(node_ids)
        assert any("Jack Bauer" == name["name"] for name in response.json().values())
        assert any("Douglas Adams" == name["name"] for name in response.json().values())
        assert any("Turkey" == name["name"] for name in response.json().values())

        # Check wheter description is not null
        assert all(len(name["description"]) > 2 for name in response.json().values())

    def test_wikidata_get_edges_nids(self, client: TestClient, wikidata_kg_name:str):
        # Given:
        url = f"/datastores/kg/{wikidata_kg_name}/edges/query_by_ids"

        # When:
        response = client.post(
            url,
            json=[["Q76", "Q11696"],["Q76", "Q13133"]]
            )

        # Then:
        assert response.status_code == 200
        assert any(rel["description"].split(";")[0] == "P26" for i, rel in response.json().items())
        assert any(rel["description"].split(";")[0] == "P39" for i, rel in response.json().items())
     

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

    def test_get_subgraph(self, client: TestClient, kg_name: str, test_node_lower: Document, token: str):
        # Given:
        url_post = f"/datastores/kg/{kg_name}/subgraph/query_by_node_name"

        # When:
        response_post = client.post(
            url_post, 
            json= {"nids": [test_node_lower["name"]], "hops": 2 },
            headers={"Authorization": f"Bearer {token}"}
        )

        # Then:
        assert response_post.status_code == 200
        assert len(response_post.json()) > 0