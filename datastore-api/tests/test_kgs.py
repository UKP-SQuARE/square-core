import asyncio
from typing import Any
from unittest.mock import MagicMock, patch
import json
from fastapi.testclient import TestClient
import ast
import pytest
from requests_mock import Mocker
from tests.utils import async_mock_callable


class TestKGs:

    def test_wikidata_get_nodes_by_names(self, client: TestClient, wikidata_kg_name:str):
        # Given:
        url = f"/datastores/kg/{wikidata_kg_name}/nodes/query_by_name"
        expeceted_code = 200

        # When:
        response = client.post(
            url,
            json = ["Barack Obama", "Bill Clinton"] )
        
        # Then:
        assert response.status_code == expeceted_code
        assert response.json() == {'Barack Obama': ['http://www.wikidata.org/entity/Q76', 'http://www.wikidata.org/entity/Q47513588', 'http://www.wikidata.org/entity/Q61909968'], 'Bill Clinton': ['http://www.wikidata.org/entity/Q1124', 'http://www.wikidata.org/entity/Q2903164', 'http://www.wikidata.org/entity/Q47508810', 'http://www.wikidata.org/entity/Q47513276', 'http://www.wikidata.org/entity/Q47513347', 'http://www.wikidata.org/entity/Q77009656']}


    def test_wikidata_get_node_by_id(self, client: TestClient, wikidata_kg_name: str):
        # Given:
        node_id = "Q42"
        url = f"/datastores/kg/{wikidata_kg_name}/{node_id}"

        # When:
        response = client.get(url)

        # Then:
        assert response.json() == {'Q42': ['http://www.wikidata.org/entity/Q28309063', 'http://www.wikidata.org/entity/Q42395533']}


    def test_wikidata_get_subgraph(self, client: TestClient, wikidata_kg_name:str):
        # Given:
        url = f"/datastores/kg/{wikidata_kg_name}/subgraph/query_by_node_name"
        expected_code = 200

        # When:
        response = client.post(
            url,
            json = ["Barack Obama", "Bill Clinton"] )

        # Then:
        assert response.status_code == expected_code
        assert response.json() == {'Barack Obama': ['http://www.wikidata.org/entity/Q76', 'http://www.wikidata.org/entity/Q47513588', 'http://www.wikidata.org/entity/Q61909968'], 'Bill Clinton': ['http://www.wikidata.org/entity/Q1124', 'http://www.wikidata.org/entity/Q2903164', 'http://www.wikidata.org/entity/Q47508810', 'http://www.wikidata.org/entity/Q47513276', 'http://www.wikidata.org/entity/Q47513347', 'http://www.wikidata.org/entity/Q77009656']}
        

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
        