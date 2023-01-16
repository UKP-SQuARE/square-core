import asyncio
from typing import Any
from unittest.mock import MagicMock, patch
import json
import ast
import pytest
from requests_mock import Mocker
from tests.utils import async_mock_callable
import ipdb

class TestKGs:

    def test_get_all_kgs(self, client):
        response = client.get("/datastores/kg")

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_conceptnet(self, client, conceptnet_kg):
        response = client.get("/datastores/kg/conceptnet")

        assert response.status_code == 200
        assert response.json() == conceptnet_kg.dict()
        assert response.content.decode() == '{"name":"conceptnet","fields":[{"name":"description","type":"text"},{"name":"in_id","type":"keyword"},{"name":"in_out_id","type":"keyword"},{"name":"name","type":"keyword"},{"name":"out_id","type":"keyword"},{"name":"type","type":"keyword"},{"name":"weight","type":"double"}]}'

    def test_get_kg_not_found(self, client):
        response = client.get("/datastores/kg/not_found")
        
        assert response.status_code == 404

    def test_delete_kg_not_found(self, client, token):
        response = client.delete(
            "/datastores/kg/not_found", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_get_kg_stats(self, client, kg_name):
        response = client.get("/datastores/kg/{}/stats".format(kg_name))

        assert response.status_code == 200
        assert "name" in response.json()
        assert "documents" in response.json()
        assert "size_in_bytes" in response.json()

