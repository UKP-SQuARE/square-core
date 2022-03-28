import logging
from typing import List, Optional

import requests

from ..models.query import QueryResult


logger = logging.getLogger(__name__)


class FaissClient:
    """Wraps access to the FAISS server."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def build_faiss_url(self, datastore_name, index_name):
        url = '_'.join(['faiss', datastore_name, index_name])
        return url

    def status(self, datastore_name, index_name) -> Optional[dict]:
        url = f"{self.build_faiss_url(datastore_name, index_name)}/index_list"
        response = requests.get(url)
        if response.status_code != 200:
            logger.info(response.text)
            return None

        queried = response.json()
        return queried

    def search(self, datastore_name, index_name, query_vector, top_k=10) -> List[QueryResult]:
        url = f"{self.build_faiss_url(datastore_name, index_name)}/search"
        data = {"k": top_k, "vectors": [query_vector]}
        logger.debug(f"querying faiss at {url}") 
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logger.info(response.text)
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")
        
        logger.debug(f"received response from datastore api:\n{response.content}")
        
        queried = response.json()[0]
        return queried

    def explain(self, datastore_name, index_name, query_vector, document_id) -> QueryResult:
        url = f"{self.build_faiss_url(datastore_name, index_name)}/explain"
        data = {"vector": query_vector, "id": document_id}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logger.info(response.text)
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()
        return queried

    def reconstruct(self, datastore_name, index_name, document_id) -> List[float]:
        url = f"{self.build_faiss_url(datastore_name, index_name)}/reconstruct"
        params = {"id": document_id}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logger.info(response.text)
            raise EnvironmentError(f"Faiss server returned {response.status_code}.")

        queried = response.json()
        return queried
