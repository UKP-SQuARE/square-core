from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Tuple

from ..models.datastore import Datastore
from ..models.document import Document
from ..models.index import Index
from ..models.query import QueryResult
from .base_class_converter import BaseClassConverter


class BaseConnector(ABC):
    """Provides an abstract interface for a connector to a datastore backend."""

    def __init__(self, converter: BaseClassConverter):
        self.converter = converter

    # --- Datastore schemas ---

    @abstractmethod
    async def get_datastores(self) -> List[Datastore]:
        """Returns a list of all datastores."""
        pass

    @abstractmethod
    async def get_datastore(self, datastore_name: str) -> Optional[Datastore]:
        """Returns a datastore by name.

        Args:
            datastore_name (str): Name of the datastore.
        """
        pass

    @abstractmethod
    async def add_datastore(self, datastore: Datastore) -> bool:
        """Adds a new datastore.

        Args:
            datastore (Datastore): Datastore to add.
        """
        pass

    @abstractmethod
    async def update_datastore(self, datastore: Datastore) -> bool:
        """Updates a datastore.

        Args:
            datastore (Datastore): Datastore to update.
        """
        pass

    @abstractmethod
    async def delete_datastore(self, datastore_name: str) -> bool:
        """Deletes a datastore.

        Args:
            datastore_name (str): Name of the datastore.
        """
        pass

    # --- Index schemas ---

    @abstractmethod
    async def get_indices(self, datastore_name: str) -> List[Index]:
        """Returns a list of all indices."""
        pass

    @abstractmethod
    async def get_index(self, datastore_name: str, index_name: str) -> Optional[Index]:
        """Returns an index by name.

        Args:
            datastore_name (str): Name of the datastore.
            index_name (str): Name of the index.
        """
        pass

    @abstractmethod
    async def add_index(self, index: Index) -> bool:
        """Adds a new index.

        Args:
            index (Index): Index to add.
        """
        pass

    @abstractmethod
    async def update_index(self, index: Index) -> Tuple[bool, bool]:
        """Updates an index.

        Args:
            index (Index): Index to update.

        Returns:
            Tuple[bool, bool]: A tuple containing the success of the update and a flag indicating whether an item was newly created.
        """
        pass

    @abstractmethod
    async def delete_index(self, datastore_name: str, index_name: str) -> bool:
        """Deletes an index.

        Args:
            datastore_name (str): Name of the datastore.
            index_name (str): Name of the index.
        """
        pass

    # --- Documents ---

    @abstractmethod
    async def get_documents(self, datastore_name: str) -> Iterable[Document]:
        """Returns a list of all documents."""
        pass

    @abstractmethod
    async def get_document(self, datastore_name: str, document_id: int) -> Optional[Document]:
        """Returns a document by id.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        pass

    @abstractmethod
    async def get_document_batch(self, datastore_name: str, document_ids: List[int]) -> List[Document]:
        """Returns a batch of documents by id.

        Args:
            datastore_name (str): Name of the datastore.
            document_ids (List[int]): Ids of the documents.
        """
        pass

    @abstractmethod
    async def add_document(self, datastore_name: str, document_id: int, document: Document) -> bool:
        """Adds a new document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to add.
        """
        pass

    @abstractmethod
    async def add_document_batch(self, datastore_name: str, documents: Iterable[Document]) -> Tuple[int, int]:
        """Adds a batch of documents.

        Args:
            datastore_name (str): Name of the datastore.
            documents (Iterable[Document]): Documents to add.

        Returns:
            Tuple[int, int]: A tuple containing the number of documents added and the number of error.
        """
        pass

    @abstractmethod
    async def update_document(self, datastore_name: str, document_id: int, document: Document) -> Tuple[bool, bool]:
        """Updates a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to update.

        Returns:
            Tuple[bool, bool]: A tuple containing the success of the update and a flag indicating whether an item was newly created.
        """
        pass

    @abstractmethod
    async def delete_document(self, datastore_name: str, document_id: int) -> bool:
        """Deletes a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        pass

    @abstractmethod
    async def has_document(self, datastore_name: str, document_id: int) -> bool:
        """Checks if a document exists.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
        """
        pass

    # --- Search ---

    @abstractmethod
    async def search(self, datastore_name: str, query: str, n_hits=10) -> List[QueryResult]:
        """Searches for documents.

        Args:
            datastore_name (str): Name of the datastore.
            query (str): Query to search for.
            n_hits (int): Number of hits to return.
        """
        pass

    @abstractmethod
    async def search_for_id(self, datastore_name: str, query: str, document_id: int):
        """Searches for documents and selects the document with the given id from the results.

        Args:
            datastore_name (str): Name of the datastore.
            query (str): Query to search for.
            document_id (int): Id of the document.
        """
        pass

    # --- Management methods ---

    @abstractmethod
    async def commit_changes(self):
        """Commits all changes. E.g., in the case of Vespa, this would export & upload an application package."""
        pass
