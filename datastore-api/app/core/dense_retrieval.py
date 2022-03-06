import logging
from typing import List
from ..models.document import Document

from ..models.query import QueryResult
from .base_connector import BaseConnector
from .faiss import FaissClient
from .model_api import ModelAPIClient

logger = logging.getLogger(__name__)

class DenseRetrieval:
    """Contains the logic for dense retrieval leveraging the Square Model API and FAISS."""

    def __init__(self, conn: BaseConnector, model_api: ModelAPIClient, faiss: FaissClient):
        self.conn = conn
        self.model_api = model_api
        self.faiss = faiss

    async def status(self, datastore_name: str, index_name: str) -> bool:
        """Checks the availability of the given index.
        This method queries both the FAISS web service and the Model API server as both are required for retrieval.

        Args:
            datastore_name (str): The datastore in which to search.
            index_name (str): The index to be used.

        Returns:
            bool: True if the index is available, False otherwise.
        """
        index = await self.conn.get_index(datastore_name, index_name)
        if index is None:
            return False

        status = self.faiss.status(datastore_name, index_name) is not None
        if status:
            status &= self.model_api.is_alive(index)
        return status

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

        #TODO: Reuse search_by_vector
        # 1. Get the query embedding from the model api
        query_vector = self.model_api.encode_query(query, index)
        logger.debug(f"Received query embedding:{query_vector}")
        # 2. Search for the query in the FAISS store. This will return ids of matched docs.
        queried = self.faiss.search(datastore_name, index_name, query_vector, top_k)
        logger.debug(f"Queried Faiss, returned {len(queried)} docs.")
        # 3. Lookup the retrieved doc ids in the ES index.
        docs: List[Document] = await self.conn.get_document_batch(datastore_name, [int(k) for k in queried.keys()])
        results = []
        for doc in docs:
            doc_id = str(doc["id"])
            results.append(QueryResult(document=doc, score=queried[doc_id], id=doc_id))

        return sorted(results, key=lambda x: x.score, reverse=True)

    async def search_by_vector(self, datastore_name: str, index_name: str, query_vector: List[float], top_k: int = 10) -> List[QueryResult]:
        """Searches for documents matching the given query vector.

        Args:
            datastore_name (str): The datastore in which to search.
            index_name (str): The index to be used.
            query_vector (list): The query vector.
            top_k (int, optional): The number of hits to return. Defaults to 10.

        Returns:
            list: A list of QueryResults.
        """
        index = await self.conn.get_index(datastore_name, index_name)
        if index is None:
            raise ValueError("Datastore or index not found.")

        # 0. Ensure the query vector has the right dimensionality.
        query_vector = query_vector + [0] * (index.embedding_size - len(query_vector))
        # 1. Search for the query in the FAISS store. This will return ids of matched docs.
        queried = self.faiss.search(datastore_name, index_name, query_vector, top_k)
        # 2. Lookup the retrieved doc ids in the ES index.
        docs: List[Document] = await self.conn.get_document_batch(datastore_name, [int(k) for k in queried.keys()])
        results = []
        for doc in docs:
            doc_id = str(doc["id"])
            results.append(QueryResult(document=doc, score=queried[doc_id], id=doc_id))

        return sorted(results, key=lambda x: x.score, reverse=True)

    async def score(self, datastore_name: str, index_name: str, query: str, document_id: str) -> QueryResult:
        """Scores a document by the given query string.

        Args:
            datastore_name (str): The datastore in which to search.
            index_name (str): The index to be used.
            query (str): The query string.
            document_id (str): The id of the document to be scored.

        Returns:
            QueryResult: The scored document.
        """
        index = await self.conn.get_index(datastore_name, index_name)
        if index is None:
            raise ValueError("Datastore or index not found.")

        # 1. Get the query embedding from the model api
        query_vector = self.model_api.encode_query(query, index)
        # 2. Search for the query in the FAISS store. This will return ids of matched docs.
        queried = self.faiss.explain(datastore_name, index_name, query_vector, document_id)
        # 3. Lookup the retrieved doc ids in the ES index.
        doc = await self.conn.get_document(datastore_name, document_id)
        return QueryResult(document=doc, score=queried["score"], id=document_id)

    async def get_document_embedding(self, datastore_name: str, index_name: str, document_id: str) -> List[float]:
        """Gets the embedding of a document.

        Args:
            datastore_name (str): The datastore in which to search.
            index_name (str): The index to be used.
            document_id (str): The id of the document.

        Returns:
            list: The embedding of the document.
        """
        index = await self.conn.get_index(datastore_name, index_name)
        if index is None:
            raise ValueError("Datastore or index not found.")

        result = self.faiss.reconstruct(datastore_name, index_name, document_id)
        return result["vector"]
