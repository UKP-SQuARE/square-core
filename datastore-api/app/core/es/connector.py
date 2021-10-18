import logging
from typing import Iterable, List, Optional, Tuple

import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk, async_scan

from ...models.datastore import Datastore
from ...models.document import Document
from ...models.index import Index
from ..base_connector import BaseConnector
from .class_converter import ElasticsearchClassConverter


logger = logging.getLogger(__name__)


class ElasticsearchConnector(BaseConnector):
    """Provides a connector for an Elasticsearch backend."""

    def __init__(self, host: str):
        """Initializes a new instance of ElasticsearchConnector.

        Args:
            host (str): Hostname of the Elasticsearch instance.
        """
        super().__init__(converter=ElasticsearchClassConverter())
        self.es = AsyncElasticsearch(hosts=[host])

    # --- Datastore schemas ---
    # Each datastore is represented by two ES indices:
    # - _datastore_docs_index_name stores the actual documents of the datastore
    # - _datastore_search_index_name stores the search indices of the datastore

    def _datastore_docs_index_name(self, datastore_name: str) -> str:
        return datastore_name + "-docs"

    def _datastore_search_index_name(self, datastore_name: str) -> str:
        return datastore_name + "-search-indices"

    async def get_datastores(self) -> List[Datastore]:
        """Returns a list of all datastores."""
        datastores = []
        indices = await self.es.indices.get(index="*-docs")
        for name, obj in indices.items():
            datastores.append(self.converter.convert_to_datastore(name, obj))

        return datastores

    async def get_datastore(self, datastore_name: str) -> Optional[Datastore]:
        """Returns a datastore by name.

        Args:
            datastore_name (str): Name of the datastore.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        try:
            index = await self.es.indices.get(index=docs_index)
            print(index)
            return self.converter.convert_to_datastore(datastore_name, index[docs_index])
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def add_datastore(self, datastore: Datastore) -> bool:
        """Adds a new datastore.

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

    async def update_datastore(self, datastore: Datastore) -> bool:
        """Updates a datastore.

        Args:
            datastore (Datastore): Datastore to update.
        """
        try:
            mappings = self.converter.convert_from_datastore(datastore)["mappings"]
            await self.es.indices.put_mapping(index=self._datastore_docs_index_name(datastore.name), body=mappings)
            return True
        except elasticsearch.exceptions.NotFoundError:
            return False

    async def delete_datastore(self, datastore_name: str) -> bool:
        """Deletes a datastore.

        Args:
            datastore_name (str): Name of the datastore.
        """
        try:
            resp1 = await self.es.indices.delete(index=self._datastore_docs_index_name(datastore_name))
            resp2 = await self.es.indices.delete(index=self._datastore_search_index_name(datastore_name))
            return resp1["acknowledged"] and resp2["acknowledged"]
        except elasticsearch.exceptions.NotFoundError:
            return False

    # --- Index schemas ---

    async def get_indices(self, datastore_name: str) -> List[Index]:
        """Returns a list of all indices.

        Args:
            datastore_name (str): Name of the datastore.
        """
        search_index_index = self._datastore_search_index_name(datastore_name)
        results = await self.es.search(
            index=search_index_index,
            body={"query": {"match_all": {}}},
            ignore_unavailable=True,
        )
        indices = []
        for hit in results["hits"]["hits"]:
            indices.append(self.converter.convert_to_index(hit["_source"]))

        return indices

    async def get_index(self, datastore_name: str, index_name: str) -> Optional[Index]:
        """Returns an index by name.

        Args:
            datastore_name (str): Name of the datastore.
            index_name (str): Name of the index.
        """
        search_index_index = self._datastore_search_index_name(datastore_name)
        try:
            result = await self.es.get(index=search_index_index, id=index_name)
            return self.converter.convert_to_index(result["_source"])
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def add_index(self, index: Index) -> bool:
        """Adds a new index.

        Args:
            index (Index): Index to add.
        """
        search_index_index = self._datastore_search_index_name(index.datastore_name)
        result = await self.es.index(
            index=search_index_index, id=index.name, body=self.converter.convert_from_index(index)
        )

        return result["_shards"]["successful"] > 0

    async def update_index(self, index: Index) -> Tuple[bool, bool]:
        """Updates an index.

        Args:
            index (Index): Index to update.

        Returns:
            Tuple[bool, bool]: A tuple containing the success of the update and a flag indicating whether an item was newly created.
        """
        search_index_index = self._datastore_search_index_name(index.datastore_name)
        result = await self.es.update(
            index=search_index_index,
            id=index.name,
            body={"doc": self.converter.convert_from_index(index)},
        )
        return result["_shards"]["successful"] > 0, result["result"] == "created"

    async def delete_index(self, datastore_name: str, index_name: str) -> bool:
        """Deletes an index.

        Args:
            datastore_name (str): Name of the datastore.
            index_name (str): Name of the index.
        """
        search_index_index = self._datastore_search_index_name(datastore_name)
        try:
            result = await self.es.delete(index=search_index_index, id=index_name)
            return result["result"] == "deleted"
        except elasticsearch.exceptions.NotFoundError:
            return False

    # --- Documents ---

    async def get_documents(self, datastore_name: str) -> Iterable[Document]:
        """Returns a list of all documents."""
        docs_index = self._datastore_docs_index_name(datastore_name)
        results = async_scan(
            client=self.es,
            index=docs_index,
            query={"query": {"match_all": {}}},
            ignore_unavailable=True,
        )

        async for hit in results:
            yield self.converter.convert_to_document(hit["_source"])

    async def get_document(self, datastore_name: str, document_id: int) -> Optional[Document]:
        """Returns a document by id.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        try:
            result = await self.es.get(index=docs_index, id=document_id)
            return self.converter.convert_to_document(result["_source"])
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def add_document(self, datastore_name: str, document_id: int, document: Document) -> bool:
        """Adds a new document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to add.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        result = await self.es.index(
            index=docs_index,
            id=document_id,
            body=self.converter.convert_from_document(document),
        )

        return result["_shards"]["successful"] > 0

    async def add_document_batch(self, datastore_name: str, documents: Iterable[Document]) -> Tuple[int, int]:
        """Adds a batch of documents.

        Args:
            datastore_name (str): Name of the datastore.
            documents (Iterable[Document]): Documents to add.

        Returns:
            Tuple[int, int]: A tuple containing the number of documents added and the number of error.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        actions = []
        for document in documents:
            actions.append(
                {
                    "_index": docs_index,
                    "_id": document["id"],
                    "_source": self.converter.convert_from_document(document),
                }
            )
        return await async_bulk(self.es, actions, stats_only=True, raise_on_error=False)

    async def update_document(self, datastore_name: str, document_id: int, document: Document) -> Tuple[bool, bool]:
        """Updates a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to update.

        Returns:
            Tuple[bool, bool]: A tuple containing the success of the update and a flag indicating whether an item was newly created.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        result = await self.es.update(
            index=docs_index,
            id=document_id,
            body={"doc": self.converter.convert_from_document(document)},
        )
        return result["_shards"]["successful"] > 0, result["result"] == "created"

    async def delete_document(self, datastore_name: str, document_id: int) -> bool:
        """Deletes a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        try:
            result = await self.es.delete(index=docs_index, id=document_id)
            return result["result"] == "deleted"
        except elasticsearch.exceptions.NotFoundError:
            return False

    async def has_document(self, datastore_name: str, document_id: int) -> bool:
        """Checks if a document exists.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        return await self.es.exists(index=docs_index, id=document_id)

    # --- Search ---

    async def search(self, datastore_name: str, query: str, n_hits=10):
        """Searches for documents.

        Args:
            datastore_name (str): Name of the datastore.
            query (str): Query to search for.
            n_hits (int): Number of hits to return.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                }
            },
            "size": n_hits,
        }
        return await self.es.search(index=docs_index, body=search_body)

    async def search_for_id(self, datastore_name: str, query: str, document_id: int):
        """Searches for documents and selects the document with the given id from the results.

        Args:
            datastore_name (str): Name of the datastore.
            query (str): Query to search for.
            document_id (int): Id of the document.
        """
        docs_index = self._datastore_docs_index_name(datastore_name)
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                }
            },
            "post_filter": {
                "term": {"id": document_id},
            },
        }
        return await self.es.search(index=docs_index, body=search_body)

    # --- Management methods ---

    async def commit_changes(self):
        """Commits all changes. E.g., in the case of Vespa, this would export & upload an application package."""
        await self.es.indices.refresh(index="")

    def __del__(self):
        self.es.close()
