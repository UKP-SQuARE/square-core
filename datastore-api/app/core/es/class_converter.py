from typing import Any, Dict, List

from ...models.datastore import Datastore, DatastoreField
from ...models.document import ID_FIELD, Document
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
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-create-index.html#indices-create-api-request-body
        index = {
            "mappings": {
                "properties": {},
            }
        }
        for field in datastore.fields:
            index["mappings"]["properties"][field.name] = {
                "type": field.type,
            }

        return index

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
        document = dict(document.__root__)
        document.pop(ID_FIELD)  # Because we do not define it in the ES index schema, while relying on the ES's inner ids
        return document

    def convert_to_document(self, obj: Dict[str, Any], document_id: str) -> Document:
        """
        Converts a backend-specific object to a document object.
        """
        obj = dict(obj)  # here the `obj` is `hit['_source']`
        obj[ID_FIELD] = document_id
        return Document(__root__=obj)

    def convert_to_query_results(self, obj: Dict[str, Any]) -> List[QueryResult]:
        """
        Converts a backend-specific object to a list of query results.
        """
        results = []
        for hit in obj["hits"]["hits"]:
            doc = self.convert_to_document(hit["_source"], hit["_id"])
            results.append(QueryResult(document=doc, score=hit["_score"], id=hit["_id"]))

        return results
