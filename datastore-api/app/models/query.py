from pydantic import BaseModel

from .document import Document


class QueryResult(BaseModel):
    """Represents one retrieved document in a list of query results."""
    document: Document
    score: float
