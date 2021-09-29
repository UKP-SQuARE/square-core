from abc import ABC, abstractmethod

from ..models.datastore import Datastore
from ..models.document import Document
from ..models.index import Index


class BaseClassConverter(ABC):
    """
    Provides an abstract interface for a class that converts between datastore api model objects and backend-specific objects.
    """

    @abstractmethod
    def convert_from_datastore(self, datastore: Datastore) -> object:
        """
        Converts a datastore object to a backend-specific object.
        """
        pass

    @abstractmethod
    def convert_to_datastore(self, datastore_name: str, obj: object) -> Datastore:
        """
        Converts a backend-specific object to a datastore object.
        """
        pass

    @abstractmethod
    def convert_from_index(self, index: Index) -> object:
        """
        Converts an index object to a backend-specific object.
        """
        pass

    @abstractmethod
    def convert_to_index(self, obj: object) -> Index:
        """
        Converts a backend-specific object to an index object.
        """
        pass

    @abstractmethod
    def convert_from_document(self, document: Document) -> object:
        """
        Converts a document object to a backend-specific object.
        """
        pass

    @abstractmethod
    def convert_to_document(self, obj: object) -> Document:
        """
        Converts a backend-specific object to a document object.
        """
        pass
