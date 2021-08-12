from typing import Dict, List

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

    @classmethod
    def from_vespa(cls, doc: Dict, embedding_name: str):
        """Reads a document embedding object from a Vespa document API response."""
        embedding = [x["value"] for x in doc["fields"][embedding_name]["cells"]]
        return cls(id=doc["id"].split(":")[-1], embedding=embedding)
