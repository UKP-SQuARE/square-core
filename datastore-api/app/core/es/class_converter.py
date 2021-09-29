from ...models.datastore import Datastore, DatastoreField
from ...models.document import Document
from ...models.index import Index
from ..base_class_converter import BaseClassConverter


class ElasticsearchClassConverter(BaseClassConverter):
    """
    Provides an abstract interface for a class that converts between datastore api model objects and backend-specific objects.
    """

    def convert_from_datastore(self, datastore: Datastore) -> object:
        """
        Converts a datastore object to a backend-specific object.
        """
        index = {
            "mappings": {
                "properties": {}
            }
        }
        for field in datastore.fields:
            index["mappings"]["properties"][field.name] = {"type": field.type}

        return index

    def convert_to_datastore(self, datastore_name: str, obj: object) -> Datastore:
        """
        Converts a backend-specific object to a datastore object.
        """
        fields = []
        for prop_name, prop_kwargs in obj["mappings"]["properties"].items():
            fields.append(DatastoreField(name=prop_name, type=prop_kwargs["type"]))
        return Datastore(name=datastore_name, fields=fields)

    def convert_from_index(self, index: Index) -> object:
        """
        Converts an index object to a backend-specific object.
        """
        return index.dict()

    def convert_to_index(self, obj: object) -> Index:
        """
        Converts a backend-specific object to an index object.
        """
        return Index(**obj)

    def convert_from_document(self, document: Document) -> object:
        """
        Converts a document object to a backend-specific object.
        """
        return document.dict()

    def convert_to_document(self, obj: object) -> Document:
        """
        Converts a backend-specific object to a document object.
        """
        return Document(**obj)
