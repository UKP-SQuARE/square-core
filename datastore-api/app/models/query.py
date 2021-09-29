from typing import Dict, List

from pydantic import BaseModel

from .document import Document


class QueryResultDocument(BaseModel):
    """Represents one retrieved document in a query result."""
    relevance: float
    document: Document

    @classmethod
    def from_vespa(cls, item: Dict, fields: List):
        return cls(
            relevance=item['relevance'],
            document=Document.from_vespa(item, fields),
        )


class QueryResult(BaseModel):
    """Models the result of querying the search endpoint of the API."""
    coverage: int
    covered_documents: int
    documents: List[QueryResultDocument]

    @classmethod
    def from_vespa(cls, item: Dict, fields: List):
        root = item["root"]
        if "children" in root:
            documents = [QueryResultDocument.from_vespa(doc, fields) for doc in root["children"]]
        else:
            documents = []
        return cls(
            coverage=root["coverage"]["coverage"] if "coverage" in root else 0,
            covered_documents=root["coverage"]["documents"] if "coverage" in root else 0,
            documents=documents,
        )
