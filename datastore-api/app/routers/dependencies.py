from functools import lru_cache

from ..core.base_connector import BaseConnector
from ..core.config import settings
from ..core.dense_retrieval import DenseRetrieval
from ..core.es.connector import ElasticsearchConnector
from ..core.kgs.connector import KnowledgeGraphConnector
from ..core.faiss import FaissClient
from ..core.model_api import ModelAPIClient
from ..core.mongo import MongoClient
# from ..core.bing import BingSearch
from ..core.wikidata import WikiData

from square_auth.client_credentials import ClientCredentials
client_credentials = ClientCredentials()  # For getting tokens and enable access to **other** servicess

# IMPORTANT: When altering this, make sure to also alter the corresponding mock in conftest.py!
@lru_cache()
def get_storage_connector() -> BaseConnector:
    return ElasticsearchConnector(settings.ES_URL)

@lru_cache()
def get_kg_storage_connector() -> ElasticsearchConnector:
    return KnowledgeGraphConnector(settings.ES_URL)


# IMPORTANT: When altering this, make sure to also alter the corresponding mock in conftest.py!
@lru_cache()
def get_search_client() -> DenseRetrieval:
    model_api = ModelAPIClient(
        settings.MODEL_API_URL
    )
    faiss = FaissClient()
    return DenseRetrieval(get_storage_connector(), model_api, faiss)

@lru_cache()
def get_mongo_client() -> MongoClient:
    return MongoClient(
        settings.MONGO_HOST, 
        settings.MONGO_PORT,
        settings.MONGO_INITDB_ROOT_USERNAME,
        settings.MONGO_INITDB_ROOT_PASSWORD,
        settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
    )

    