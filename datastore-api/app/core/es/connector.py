from typing import List, Optional

import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch

from ...models.datastore import Datastore
from ...models.document import Document
from ...models.index import Index
from ..base_connector import BaseConnector
from .class_converter import ElasticsearchClassConverter


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

    def _get_datastore_search_index_name(self, datastore_name: str) -> str:
        return datastore_name + "-search-indices"  # TODO make sure names of this form aren't used as datastore names

    async def get_datastores(self) -> List[Datastore]:
        """Returns a list of all datastores."""
        datastores = []
        indices = await self.es.indices.get(index="*")
        for name, obj in indices.items():
            datastores.append(self.converter.convert_to_datastore(name, obj))

        return datastores

    async def get_datastore(self, datastore_name: str) -> Optional[Datastore]:
        """Returns a datastore by name.

        Args:
            datastore_name (str): Name of the datastore.
        """
        try:
            index = await self.es.indices.get(index=datastore_name)
            return self.converter.convert_to_datastore(datastore_name, index[datastore_name])
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def add_datastore(self, datastore: Datastore):
        """Adds a new datastore.

        Args:
            datastore (Datastore): Datastore to add.
        """
        # The ES index that holds the documents
        await self.es.indices.create(index=datastore.name, body=self.converter.convert_from_datastore(datastore))
        # The ES index that holds the (FAISS) search index config
        await self.es.indices.create(index=self._get_datastore_search_index_name(datastore.name), body={})

    async def update_datastore(self, datastore: Datastore) -> bool:
        """Updates a datastore.

        Args:
            datastore (Datastore): Datastore to update.
        """
        try:
            mappings = self.converter.convert_from_datastore(datastore)["mappings"]
            await self.es.indices.put_mapping(index=datastore.name, body=mappings)
            return True
        except elasticsearch.exceptions.NotFoundError:
            return False

    async def delete_datastore(self, datastore_name: str) -> bool:
        """Deletes a datastore.

        Args:
            datastore_name (str): Name of the datastore.
        """
        try:
            result1 = await self.es.indices.delete(index=datastore_name)
            result2 = await self.es.indices.delete(index=self._get_datastore_search_index_name(datastore_name))
            return result1 == "deleted" and result2 == "deleted"
        except elasticsearch.exceptions.NotFoundError:
            return False

    # --- Index schemas ---

    async def get_indices(self, datastore_name: str, limit: int = None) -> List[Index]:
        """Returns a list of all indices.

        Args:
            datastore_name (str): Name of the datastore.
            limit (int, optional): Maximal number of items to return. Defaults to None.
        """
        search_index_index = self._get_datastore_search_index_name(datastore_name)
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
        search_index_index = self._get_datastore_search_index_name(datastore_name)
        try:
            result = await self.es.get(index=search_index_index, id=index_name)
            return self.converter.convert_to_index(result["_source"])
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def add_index(self, index: Index):
        """Adds a new index.

        Args:
            index (Index): Index to add.
        """
        search_index_index = self._get_datastore_search_index_name(index.datastore_name)
        await self.es.index(index=search_index_index, id=index.name, body=self.converter.convert_from_index(index))

    async def update_index(self, index: Index) -> bool:
        """Updates an index.

        Args:
            index (Index): Index to update.
        """
        search_index_index = self._get_datastore_search_index_name(index.datastore_name)
        result = await self.es.update(
            index=search_index_index,
            id=index.name,
            body={"doc": self.converter.convert_from_index(index)},
        )
        return result["result"] != "noop"

    async def delete_index(self, datastore_name: str, index_name: str) -> bool:
        """Deletes an index.

        Args:
            datastore_name (str): Name of the datastore.
            index_name (str): Name of the index.
        """
        search_index_index = self._get_datastore_search_index_name(datastore_name)
        try:
            result = await self.es.delete(index=search_index_index, id=index_name)
            return result["result"] == "deleted"
        except elasticsearch.exceptions.NotFoundError:
            return False

    # --- Documents ---

    async def get_documents(self, datastore_name: str) -> List[Document]:
        """Returns a list of all documents."""
        results = await self.es.search(
            index=datastore_name,
            body={"query": {"match_all": {}}},
            ignore_unavailable=True,
        )
        docs = []
        for hit in results["hits"]["hits"]:
            docs.append(self.converter.convert_to_document(hit["_source"]))

        return docs

    async def get_document(self, datastore_name: str, document_id: int) -> Optional[Document]:
        """Returns a document by id.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        try:
            result = await self.es.get(index=datastore_name, id=document_id)
            return self.converter.convert_to_document(result["_source"])
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def add_document(self, datastore_name: str, document_id: int, document: Document):
        """Adds a new document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to add.
        """
        await self.es.index(
            index=datastore_name,
            id=document_id,
            body=self.converter.convert_from_document(document),
        )

    async def update_document(self, datastore_name: str, document_id: int, document: Document) -> bool:
        """Updates a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to update.
        """
        result = await self.es.update(
            index=datastore_name,
            id=document_id,
            body={"doc": self.converter.convert_from_document(document)},
        )
        return result["result"] != "noop"

    async def delete_document(self, datastore_name: str, document_id: int) -> bool:
        """Deletes a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        try:
            result = await self.es.delete(index=datastore_name, id=document_id)
            return result["result"] == "deleted"
        except elasticsearch.exceptions.NotFoundError:
            return False

    async def has_document(self, datastore_name: str, document_id: int) -> bool:
        """Checks if a document exists.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        return await self.es.exists(index=datastore_name, id=document_id)

    # --- Management methods ---

    async def commit_changes(self):
        """Commits all changes. E.g., in the case of Vespa, this would export & upload an application package."""
        await self.es.indices.refresh(index="")

    def __del__(self):
        self.es.close()
