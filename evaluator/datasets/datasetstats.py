from pydantic import BaseModel

class DatastoreStats(BaseModel):
    """Represents statistics for a datastore."""

    name: str
    skill_type: str
    metric: str
    mapping: dict

    class Config:
        schema_extra = {
            "example": {
                "name": "test",
                "skill_type": "test",
                "metric": "accuracy",
                "mapping": {}
            }
        }
