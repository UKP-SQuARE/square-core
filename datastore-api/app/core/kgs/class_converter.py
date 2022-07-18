from typing import Any, Dict, List

from ...models.datastore import Datastore, DatastoreField
from ...models.document import ID_FIELD, Document
from ...models.index import Index
from ...models.query import QueryResult
from ..es.class_converter import ElasticsearchClassConverter

class KnowledgeGraphClassConverter(ElasticsearchClassConverter):
    """
    Provides an abstract interface for a class that converts between datastore api model objects and backend-specific objects.
    """

    def convert_to_datastore(self, datastore_name: str, obj: Dict[str, Any]) -> Datastore:
        """
        Converts a backend-specific object to a datastore object.
        """
        fields = []
        for prop_name, prop_kwargs in obj["mappings"]["properties"].items():
            fields.append(
                DatastoreField(name=prop_name, type=prop_kwargs["type"])
            )
        return Datastore(name=datastore_name, fields=fields)