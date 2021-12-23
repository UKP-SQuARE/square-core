from typing import Any, Dict, List

from ...models.datastore import Datastore, DatastoreField
from ...models.document import Document
from ...models.index import Index
from ...models.query import QueryResult
from ..base_class_converter import BaseClassConverter


class ElasticsearchClassConverter(BaseClassConverter):
    """
    Provides an abstract interface for a class that converts between datastore api model objects and backend-specific objects.
    """

    def convert_from_datastore(self, datastore: Datastore) -> Dict[str, Any]:
        """
        Converts a datastore object to a backend-specific object.
        """
        index = {
            "mappings": {
                "properties": {},
            }
        }
        for field in datastore.fields:
            index["mappings"]["properties"][field.name] = {
                "type": field.type,
                # We store additional datastore information in the meta mapping of ES.
                "meta": {"is_id": "1" if field.is_id else "0"},
            }

        return index

    def convert_to_datastore(self, datastore_name: str, obj: Dict[str, Any]) -> Datastore:
        """
        Converts a backend-specific object to a datastore object.
        """
        fields = []
        for prop_name, prop_kwargs in obj["mappings"]["properties"].items():
            is_id = False
            if "meta" in prop_kwargs:
                is_id = prop_kwargs["meta"].get("is_id", None) == "1"
            fields.append(
                DatastoreField(name=prop_name, type=prop_kwargs["type"], is_id=is_id)
            )
        return Datastore(name=datastore_name, fields=fields)

    def convert_from_index(self, index: Index) -> Dict[str, Any]:
        """
        Converts an index object to a backend-specific object.
        """
        return index.dict()

    def convert_to_index(self, obj: Dict[str, Any]) -> Index:
        """
        Converts a backend-specific object to an index object.
        """
        return Index(**obj)

    def convert_from_document(self, document: Document) -> Dict[str, Any]:
        """
        Converts a document object to a backend-specific object.
        """
        return document.__root__

    def convert_to_document(self, obj: Dict[str, Any]) -> Document:
        """
        Converts a backend-specific object to a document object.
        """
        return Document(__root__=obj)

    def convert_to_query_results(self, obj: Dict[str, Any]) -> List[QueryResult]:
        """
        Converts a backend-specific object to a list of query results.
        """
        results = []
        for hit in obj["hits"]["hits"]:
            doc = self.convert_to_document(hit["_source"])
            results.append(QueryResult(document=doc, score=hit["_score"]))

        return results
