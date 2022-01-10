from collections.abc import Mapping
from typing import Any, Dict

from pydantic import BaseModel


class Document(Mapping, BaseModel):
    __root__: Dict[str, Any]

    def __iter__(self):
        return self.__root__.__iter__()

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self):
        return len(self.__root__)

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "title": "The document title.",
                "text": "Some text of the document."
            }
        }
