from collections.abc import Iterable
from typing import List

from pydantic import BaseModel


class DatastoreField(BaseModel):
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

    class Config:
        schema_extra = {
            "example": {
                "name": "wiki",
                "fields": [
                    DatastoreField(name="id", type="long"),
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

    class Config:
        schema_extra = {
            "example": [
                DatastoreField(name="id", type="long"),
                DatastoreField(name="title", type="text"),
                DatastoreField(name="text", type="text"),
            ]
        }

    def to_datastore(self, datastore_name) -> Datastore:
        return Datastore(name=datastore_name, fields=self.__root__)
