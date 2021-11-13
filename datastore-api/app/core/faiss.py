from typing import List

import requests

from ..models.query import QueryResult


class FaissClient:
    """Wraps access to the FAISS server."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def search(self, datastore_name, index_name, query_embedding, top_k=10) -> List[QueryResult]:
        # TODO: currently always accesses the same faiss storage
        url = f"{self.base_url}/{datastore_name}/search"
        data = {"k": top_k, "vectors": [query_embedding]}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(response.json())
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()[0]
        return queried
