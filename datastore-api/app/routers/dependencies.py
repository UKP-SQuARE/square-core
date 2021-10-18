from functools import lru_cache

from ..core.base_connector import BaseConnector
from ..core.config import settings
from ..core.es.connector import ElasticsearchConnector


@lru_cache
def get_storage_connector() -> BaseConnector:
    return ElasticsearchConnector(settings.ES_URL)
