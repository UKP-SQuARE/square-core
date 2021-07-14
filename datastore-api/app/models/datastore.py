from pydantic import BaseModel
from typing import List, Optional
from vespa.package import Field, Schema


class DatastoreField(BaseModel):
    name: str
    type: str
    indexing: Optional[List[str]] = None
    index: Optional[str] = None
    attribute: Optional[List[str]] = None

    def to_vespa(self) -> Field:
        return Field(
            name=self.name,
            type=self.type,
            indexing=self.indexing,
            index=self.index,
            attribute=self.attribute
        )

    @staticmethod
    def from_vespa(field: Field):
        return DatastoreField(
            name=field.name,
            type=field.type,
            indexing=field.indexing,
            index=field.index,
            attribute=field.attribute,
        )


class Datastore(BaseModel):
    name: str
    fields: List[DatastoreField]

    @staticmethod
    def from_vespa(schema: Schema):
        return Datastore(
            name=schema.name,
            fields=[DatastoreField.from_vespa(f) for f in schema.document.fields]
        )
