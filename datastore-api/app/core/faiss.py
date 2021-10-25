from typing import List

import requests

from ..models.query import QueryResult
from .base_connector import BaseConnector


class FaissClient:
    def __init__(self, base_url: str, conn: BaseConnector):
        self.base_url = base_url
        self.conn = conn

    async def search(self, datastore_name, index_name, query_embedding, top_k=10) -> List[QueryResult]:
        # TODO: currently always accesses the same faiss storage
        url = self.base_url + "/search"
        data = {"k": top_k, "vectors": [query_embedding]}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(response.json())
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()[0]
        docs = await self.conn.get_document_batch(datastore_name, list(queried.keys()))
        results = []
        for doc in docs:
            results.append(QueryResult(document=doc, score=queried[str(doc["id"])]))

        return sorted(results, key=lambda x: x.score, reverse=True)
