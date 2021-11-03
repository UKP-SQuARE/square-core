from typing import List

from ..models.query import QueryResult
from .base_connector import BaseConnector
from .faiss import FaissClient
from .model_api import ModelAPIClient


class DenseRetrieval:
    """Contains the logic for dense retrieval leveraging the Square Model API and FAISS."""

    def __init__(self, conn: BaseConnector, model_api: ModelAPIClient, faiss: FaissClient):
        self.conn = conn
        self.model_api = model_api
        self.faiss = faiss

    async def search(self, datastore_name: str, index_name: str, query: str, top_k: int = 10) -> List[QueryResult]:
        """Searches for documents matching the given query string.

        Args:
            datastore_name (str): The datastore in which to search.
            index_name (str): The index to be used.
            query (str): The query string.
            top_k (int, optional): The number of hits to return. Defaults to 10.

        Returns:
            list: A list of QueryResults.
        """
        index = await self.conn.get_index(datastore_name, index_name)
        if index is None:
            raise ValueError("Datastore or index not found.")

        # 1. Get the query embedding from the model api
        query_embedding = self.model_api.encode_query(query, index)
        # 2. Search for the query in the FAISS store. This will return ids of matched docs.
        queried = self.faiss.search(datastore_name, index_name, query_embedding, top_k)
        # 3. Lookup the retrieved doc ids in the ES index.
        docs = await self.conn.get_document_batch(datastore_name, list(queried.keys()))
        results = []
        for doc in docs:
            results.append(QueryResult(document=doc, score=queried[str(doc["id"])]))

        return sorted(results, key=lambda x: x.score, reverse=True)
