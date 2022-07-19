from typing import List

from pydantic import BaseModel


class DocumentEmbedding(BaseModel):
    """Models the embeddings for one document."""
    id: str
    embedding: List[float]

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            }
        }
