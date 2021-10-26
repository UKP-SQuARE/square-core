from pydantic import BaseModel
from typing import List


class UploadUrlSet(BaseModel):
    urls: List[str]

    class Config:
        schema_extra = {
            "example": {
                "urls": [
                    "http://localhost:3000/documents/0.jsonl",
                ]
            }
        }


class UploadResponse(BaseModel):
    message: str
    successful_uploads: int
