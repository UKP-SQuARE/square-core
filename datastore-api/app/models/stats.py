from pydantic import BaseModel


class DatastoreStats(BaseModel):
    """Represents statistics for a datastore."""

    name: str
    documents: int
    size_in_bytes: int

    class Config:
        schema_extra = {
            "example": {
                "name": "test",
                "documents": 10,
                "size_in_bytes": 1280,
            }
        }
