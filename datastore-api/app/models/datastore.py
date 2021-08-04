from pydantic import BaseModel
from typing import List
from vespa.package import Field, Schema, FieldSet

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

    @staticmethod
    def from_vespa(field: Field):
        return DatastoreField(
            name=field.name,
            type=field.type,
            indexing=field.indexing,
            index=field.index,
            attribute=field.attribute,
        )


class DatastoreFieldSet(BaseModel):
    name: str
    fields: List[str]

    @staticmethod
    def from_vespa(fieldset: FieldSet):
        return DatastoreFieldSet(name=FIELDSET_NAME, fields=fieldset.fields)

    def to_vespa(self):
        return FieldSet(name=FIELDSET_NAME, fields=self.fields)


class Datastore(BaseModel):
    name: str
    fields: List[DatastoreField]
    fieldsets: List[DatastoreFieldSet]

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

    @staticmethod
    def from_vespa(schema: Schema):
        return Datastore(
            name=schema.name,
            fields=[DatastoreField.from_vespa(f) for f in schema.document.fields],
            fieldsets=[DatastoreFieldSet.from_vespa(f) for f in schema.fieldsets.values()]
        )
