from collections.abc import Iterable
from typing import List

from pydantic import BaseModel, validator

from .document import ID_FIELD, Document


class DatastoreField(BaseModel):
    """Model one field in a datastore schema.

    The data types are directly forwarded to Elasticsearch.
    See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html for supported types.
    """
    name: str
    type: str

    class Config:
        schema_extra = {
            "example": {
                "name": "text",
                "type": "text",
            }
        }


class Datastore(BaseModel):
    """Models one datastore schema."""
    name: str
    fields: List[DatastoreField]

    @property
    def field_names(self) -> List[str]:
        return [field.name for field in self.fields]

    def is_valid_document(self, document: Document) -> bool:
        if ID_FIELD not in document:
            return False

        fields = self.field_names
        for field in document:
            if field not in fields:
                return False

        return True

    class Config:
        schema_extra = {
            "example": {
                "name": "wiki",
                "fields": [
                    DatastoreField(name="title", type="text"),
                    DatastoreField(name="text", type="text"),
                ]
            }
        }


class DatastoreRequest(Iterable, BaseModel):
    """Models a datastore as requested by the user. Used when creating Datastores"""
    __root__: List[DatastoreField]

    def __iter__(self):
        return self.__root__.__iter__()

    class Config:
        schema_extra = {
            "example": [
                DatastoreField(name="title", type="text"),
                DatastoreField(name="text", type="text"),
            ]
        }

    def to_datastore(self, datastore_name) -> Datastore:
        return Datastore(name=datastore_name, fields=self.__root__)
