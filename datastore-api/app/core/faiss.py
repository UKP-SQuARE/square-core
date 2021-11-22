from typing import List

import requests

from ..models.query import QueryResult


class FaissClient:
    """Wraps access to the FAISS server."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def search(self, datastore_name, index_name, query_vector, top_k=10) -> List[QueryResult]:
        url = f"{self.base_url}/{datastore_name}/{index_name}/search"
        data = {"k": top_k, "vectors": [query_vector]}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(response.json())
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()[0]
        return queried

    async def explain(self, datastore_name, index_name, query_vector, document_id) -> QueryResult:
        url = f"{self.base_url}/{datastore_name}/{index_name}/explain"
        data = {"vector": query_vector, "id": document_id}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(response.json())
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()
        return queried

    async def reconstruct(self, datastore_name, index_name, document_id) -> List[float]:
        url = f"{self.base_url}/{datastore_name}/{index_name}/reconstruct"
        params = {"id": document_id}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(response.json())
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()
        return queried
