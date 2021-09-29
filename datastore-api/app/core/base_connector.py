from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.datastore import Datastore
from ..models.document import Document
from ..models.index import Index
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
    async def add_datastore(self, datastore: Datastore):
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
    async def add_index(self, index: Index):
        """Adds a new index.

        Args:
            index (Index): Index to add.
        """
        pass

    @abstractmethod
    async def update_index(self, index: Index) -> bool:
        """Updates an index.

        Args:
            index (Index): Index to update.
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
    async def get_documents(self, datastore_name: str) -> List[Document]:
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
    async def add_document(self, datastore_name: str, document_id: int, document: Document):
        """Adds a new document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to add.
        """
        pass

    @abstractmethod
    async def update_document(self, datastore_name: str, document_id: int, document: Document) -> bool:
        """Updates a document.

        Args:
            datastore_name (str): Name of the datastore.
            document_id (int): Id of the document.
            document (Document): Document to update.
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

    # --- Management methods ---

    @abstractmethod
    async def commit_changes(self):
        """Commits all changes. E.g., in the case of Vespa, this would export & upload an application package."""
        pass
