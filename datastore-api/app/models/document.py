from collections.abc import Mapping
from typing import Any, Dict

from pydantic import BaseModel, Field


ID_FIELD = 'id'

class Document(Mapping, BaseModel):
    __root__: Dict[str, Any] 

    def __init__(self, __root__):
        assert ID_FIELD in __root__, "A document must have its id"
        super(Document, self).__init__(__root__=__root__)

    @property
    def id(self):
        return self[ID_FIELD]

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
