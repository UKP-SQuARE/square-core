from functools import lru_cache

from ..core.base_connector import BaseConnector
from ..core.config import settings
from ..core.es.connector import ElasticsearchConnector
from ..core.faiss import FaissClient


@lru_cache
def get_storage_connector() -> BaseConnector:
    return ElasticsearchConnector(settings.ES_URL)


@lru_cache
def get_search_client() -> FaissClient:
    return FaissClient(settings.FAISS_URL, get_storage_connector())
