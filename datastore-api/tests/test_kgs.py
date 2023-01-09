import asyncio
from typing import Any
from unittest.mock import MagicMock, patch
import json

import ast
import pytest
from requests_mock import Mocker
from tests.utils import async_mock_callable


class TestKGs:

    def test_wikidata_get_nodes_by_names(self, client, wikidata_kg_name):
        response = client.post(
            f"/datastores/kg/{wikidata_kg_name}/nodes/query_by_name",
            json = ["Barack Obama", "Bill Clinton"] )
        
        assert response.status_code == 200
        assert  ast.literal_eval(response.content.decode()) == {"Bill Clinton":["http://www.wikidata.org/entity/Q1124","http://www.wikidata.org/entity/Q2903164","http://www.wikidata.org/entity/Q47508810","http://www.wikidata.org/entity/Q47513276","http://www.wikidata.org/entity/Q47513347","http://www.wikidata.org/entity/Q77009656"],"Barack Obama":["http://www.wikidata.org/entity/Q76","http://www.wikidata.org/entity/Q47513588","http://www.wikidata.org/entity/Q61909968"]}
    
    def test_wikidata_get_subgraph(self, client, wikidata_kg_name):
        response = client.post(
            f"/datastores/kg/{wikidata_kg_name}/subgraph/query_by_node_name",
            json = ["Barack Obama", "Bill Clinton"] )

        assert response.status_code == 200
        true_value = {'Barack Obama': ['http://www.wikidata.org/entity/Q76', 'http://www.wikidata.org/entity/Q47513588', 'http://www.wikidata.org/entity/Q61909968'], 'Bill Clinton': ['http://www.wikidata.org/entity/Q1124', 'http://www.wikidata.org/entity/Q2903164', 'http://www.wikidata.org/entity/Q47508810', 'http://www.wikidata.org/entity/Q47513276', 'http://www.wikidata.org/entity/Q47513347', 'http://www.wikidata.org/entity/Q77009656']}
        prediction = ast.literal_eval(response.content.decode())
        assert prediction == true_value