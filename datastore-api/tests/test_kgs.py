from typing import Any
from unittest.mock import MagicMock, patch
import json
from fastapi.testclient import TestClient
import ast


class TestKGs:

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
 