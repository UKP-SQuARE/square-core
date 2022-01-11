from typing import List

from pydantic import BaseModel


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
    errors: int = 0
