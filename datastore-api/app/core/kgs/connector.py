import json
import logging
from typing import Dict, Iterable, List, Optional, Tuple


import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk, async_scan


from ...core.config import settings
from ...models.datastore import Datastore
from ...models.document import Document
from ...models.index import Index
from ...models.query import QueryResult
from ...models.stats import DatastoreStats
from .class_converter import ElasticsearchClassConverter

from ...core.es.connector import ElasticsearchConnector
from .class_converter import KnowledgeGraphClassConverter

logger = logging.getLogger(__name__)


class KnowledgeGraphConnector(ElasticsearchConnector):
    """Provides a connector for an KnowledgeGraphConnector backend."""

    datastore_suffix = "-kg-docs"
    datastore_search_suffix = "-kg-search-indices"

    def __init__(self, host: str):
        """Initializes a new instance of KnowledgeGraphConnector.

        Args:
            host (str): Hostname of the Elasticsearch instance.
        """
        super().__init__(converter=KnowledgeGraphClassConverter(), host=host)


    async def get_kgs(self) -> List[Datastore]:
        """Returns a list of all knowledge graphs."""
        return await self.get_datastores()
        
    async def get_kg(self, kg_name: str) -> Optional[Datastore]:
        """Returns a knowledge graph by name.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        return await self.get_datastore(kg_name)

    async def add_kg(self, kg_name: Datastore) -> bool:
        """Adds a new knowledge graph.

        Args:
            Knowledge graph (Datastore): Knowledge graph to add.
        """
        return await self.add_datastore(kg_name)

    async def delete_kg(self, kg_name: Datastore) -> bool:
        """Deletes a knowledge graph.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        return await self.delete_datastore(kg_name)
        
    async def get_kg_stats(self, kg_name: Datastore) -> bool:
        """Returns statistics about a knowledge graph.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        return await self.get_datastore_stats(kg_name)

    async def get_all_relations(self, kg_name: Datastore) -> List[Dict[str,int]]:
        """Returns all relation names about a knowledge graph.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        docs_index = self._datastore_docs_index_name(kg_name)
        body = {
            "aggs": {
                "all_relations": {            
                    "filter": {
                        "term": {"type": "node"},
                    },
                    "aggs": {
                        "name": {
                            "terms": {"field": "name", "size": 10000}
                        }
                    }
                }
            }
        } 
        results = await self.es.search(index=docs_index, body=body)
        relations = results['aggregations']['all_relations']['name']['buckets']
        return relations