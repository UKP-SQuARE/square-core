from collections.abc import Iterable
from typing import List

from pydantic import BaseModel, validator
from vespa.package import Document, Field, FieldSet, Schema


FIELDSET_NAME = "default"


class DatastoreField(BaseModel):
    name: str
    type: str
    use_for_ranking: bool = True
    return_with_document: bool = True

    class Config:
        schema_extra = {
            "example": {
                "name": "text",
                "type": "string",
            }
        }

    def to_vespa(self) -> Field:
        indexing = []
        if self.return_with_document:
            indexing.append("summary")
        if self.use_for_ranking:
            indexing += ["attribute", "index"]

        return Field(
            name=self.name,
            type=self.type,
            indexing=indexing,
            index="enable-bm25" if self.use_for_ranking else "",
            attribute=[]
        )

    @classmethod
    def from_vespa(cls, field: Field):
        return cls(
            name=field.name,
            type=field.type,
            use_for_ranking="index" in field.indexing,
            return_with_document="summary" in field.indexing,
        )


class DatastoreFieldSet(BaseModel):
    name: str
    fields: List[str]

    @staticmethod
    def from_vespa(fieldset: FieldSet):
        return DatastoreFieldSet(name=FIELDSET_NAME, fields=fieldset.fields)

    def to_vespa(self):
        return FieldSet(name=FIELDSET_NAME, fields=self.fields)


class DatastoreRequest(Iterable, BaseModel):
    """Models a datastore as requested by the user."""
    __root__: List[DatastoreField]

    def __iter__(self):
        return self.__root__.__iter__()

    @validator("__root__")
    def cannot_contain_id(cls, v):
        for field in v:
            if field.name == "id":
                raise ValueError("Cannot use reserved field 'id'.")
        return v

    class Config:
        schema_extra = {
            "example": [
                DatastoreField(name="title", type="string"),
                DatastoreField(name="text", type="string"),
            ]
        }

    def to_vespa(self, datastore_name) -> Schema:
        schema = Schema(datastore_name, Document())
        # add default id field
        schema.add_fields(Field("id", "long", indexing=["summary", "attribute"]))
        # add all custom fields
        schema.add_fields(*[field.to_vespa() for field in self])
        # create a fieldset with all fields that could be used for ranking
        schema.add_field_set(FieldSet(FIELDSET_NAME, [f.name for f in self if f.use_for_ranking]))
        return schema


class DatastoreResponse(BaseModel):
    """Models a datastore as returned to the user."""
    name: str
    fields: List[DatastoreField]

    class Config:
        schema_extra = {
            "example": {
                "name": "wiki",
                "fields": [
                    DatastoreField(name="title", type="string"),
                    DatastoreField(name="text", type="string"),
                ]
            }
        }

    @classmethod
    def from_vespa(cls, schema: Schema):
        return cls(
            name=schema.name,
            fields=[DatastoreField.from_vespa(f) for f in schema.document.fields],
        )
