import typing
import logging
from typing import Iterable, List, Optional, Tuple

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

    def __init__(self, host: str):
        """Initializes a new instance of KnowledgeGraphConnector.

        Args:
            host (str): Hostname of the Elasticsearch instance.
        """
        super().__init__(converter=KnowledgeGraphClassConverter(), host=host)



    async def get_kgs(self) -> List[Datastore]:
        return await self.get_datastores()
        

    async def add_kg(self, datastore: Datastore) -> bool:
        """Adds a new knowledge graph.

        Args:
            datastore (Datastore): Datastore to add.
        """
        try:
            # The ES index that holds the documents
            resp1 = await self.es.indices.create(
                index=self._datastore_docs_index_name(datastore.name),
                body=self.converter.convert_from_datastore(datastore),
            )
            # The ES index that holds the (FAISS) search index config
            resp2 = await self.es.indices.create(index=self._datastore_search_index_name(datastore.name), body={})
            return resp1["acknowledged"] and resp2["acknowledged"]
        except elasticsearch.exceptions.RequestError as e:
            logger.info(e)
            return False


