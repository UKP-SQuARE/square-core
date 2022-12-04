from collections.abc import Iterable
from typing import List

from pydantic import BaseModel


class DatasetField(BaseModel):
    """Model one field in a dataset schema.

    """
    name: str
    skill_type: str
    metric: str
    mapping: dict
    """{
        id_column: int,
        question_column: int,
        context_column: str,
        answer_column: str

    }
    """

    class Config:
        schema_extra = {
            "example": {
                "dataset_name": "text",
                "skill_type": "text",
                "metric": "text_metric",
                "mapping": "text_mapping"
            }
        }


class Dataset(BaseModel):
    """Models one datastore schema."""
    name: str
    fields: List[DatasetField]

    @property
    def names(self) -> List[str]:
        return [field.name for field in self.fields]

    @property
    def skill_type(self) -> List[str]:
        return [field.skill_type for field in self.fields]

    @property
    def metric(self) -> List[str]:
        return [field.metric for field in self.fields]

    @property
    def maping_object(self) -> List[dict]:
        return [field.mapping for field in self.fields]


class DatasetRequest(Iterable, BaseModel):
    """Models a dataset as requested by the user. Used when creating Dataset"""
    __root__: List[Dataset]

    def __iter__(self):
        return self.__root__.__iter__()

    class Config:
        schema_extra = {
            "example": [
                DatasetField(name="name", skill_type="text", metric="metric_text"),
                DatasetField(name="test", skill_type="test", metric="metric_text"),
            ]
        }
