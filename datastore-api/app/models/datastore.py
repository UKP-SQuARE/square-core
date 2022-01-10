from collections.abc import Iterable
from typing import List

from pydantic import BaseModel, validator

from .document import Document


class DatastoreField(BaseModel):
    """Model one field in a datastore schema.

    The data types are directly forwarded to Elasticsearch.
    See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html for supported types.
    """
    name: str
    type: str
    is_id: bool = False

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
    def id_field(self) -> DatastoreField:
        """Return the id field of the datastore."""
        return next(
            (field for field in self.fields if field.is_id),
            None,
        )

    @property
    def field_names(self) -> List[str]:
        return [field.name for field in self.fields]

    def is_valid_document(self, document: Document) -> bool:
        if self.id_field.name not in document:
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
                    DatastoreField(name="id", type="long", is_id=True),
                    DatastoreField(name="title", type="text"),
                    DatastoreField(name="text", type="text"),
                ]
            }
        }


class DatastoreRequest(Iterable, BaseModel):
    """Models a datastore as requested by the user."""
    __root__: List[DatastoreField]

    def __iter__(self):
        return self.__root__.__iter__()

    @validator("__root__")
    def id_must_be_unique(cls, v):
        id_found = False
        for field in v:
            if field.is_id:
                if id_found:
                    raise ValueError("Only one field can be an id.")
                id_found = True
        if not id_found:
            raise ValueError("At least one field must be an id.")

        return v

    class Config:
        schema_extra = {
            "example": [
                DatastoreField(name="id", type="long", is_id=True),
                DatastoreField(name="title", type="text"),
                DatastoreField(name="text", type="text"),
            ]
        }

    def to_datastore(self, datastore_name) -> Datastore:
        return Datastore(name=datastore_name, fields=self.__root__)
