from typing import Iterable, List, Optional, Tuple

from app.core.base_connector import BaseConnector
from app.models.datastore import Datastore
from app.models.document import Document
from app.models.index import Index
from app.models.query import QueryResult
from app.models.stats import DatastoreStats


class MockConnector(BaseConnector):
    """Provides a mock datastore backend interface that keeps all data in local lists."""

    def __init__(self, datastores, indices, documents, query_document=None):
        super().__init__(None)
        self.datastores = datastores
        self.indices = indices
        self.documents = documents
        self.query_document = query_document

    async def get_datastores(self) -> List[Datastore]:
        return self.datastores

    async def get_datastore(self, datastore_name: str) -> Optional[Datastore]:
        retrieved = [d for d in self.datastores if d.name == datastore_name]
        return retrieved[0] if retrieved else None

    async def add_datastore(self, datastore: Datastore) -> bool:
        self.datastores.append(datastore)
        return True

    async def update_datastore(self, datastore: Datastore) -> bool:
        to_update = [d for d in self.datastores if d.name == datastore.name]
        if to_update:
            self.datastores.remove(to_update[0])
        self.datastores.append(datastore)
        return True

    async def delete_datastore(self, datastore_name: str) -> bool:
        to_remove = [d for d in self.datastores if d.name == datastore_name]
        if to_remove:
            self.datastores.remove(to_remove[0])
            return True
        else:
            return False

    async def get_datastore_stats(self, datastore_name: str) -> Optional[DatastoreStats]:
        return DatastoreStats(name=datastore_name, documents=0, size_in_bytes=0)

    # --- Index schemas ---

    async def get_indices(self, datastore_name: str) -> List[Index]:
        return self.indices

    async def get_index(self, datastore_name: str, index_name: str) -> Optional[Index]:
        retrieved = [i for i in self.indices if i.name == index_name]
        return retrieved[0] if retrieved else None

    async def add_index(self, index: Index) -> bool:
        self.indices.append(index)
        return True

    async def update_index(self, index: Index) -> Tuple[bool, bool]:
        to_update = [i for i in self.indices if i.name == index.name]
        if to_update:
            self.indices.remove(to_update[0])
        self.indices.append(index)
        return (True, True)

    async def delete_index(self, datastore_name: str, index_name: str) -> bool:
        to_remove = [i for i in self.indices if i.name == index_name]
        if to_remove:
            self.indices.remove(to_remove[0])
            return True
        else:
            return False

    # --- Documents ---

    async def get_documents(self, datastore_name: str) -> Iterable[Document]:
        for document in self.documents:
            yield document

    async def get_document(self, datastore_name: str, document_id: str) -> Optional[Document]:
        retrieved = [d for d in self.documents if d["id"] == document_id]
        return retrieved[0] if retrieved else None

    async def get_document_batch(self, datastore_name: str, document_ids: List[str]) -> List[Document]:
        return [d for d in self.documents if d["id"] in document_ids]

    async def add_document(self, datastore_name: str, document_id: str, document: Document) -> Tuple[bool, bool]:
        self.documents.append(document)
        return (True, True)

    async def add_document_batch(self, datastore_name: str, documents: Iterable[Document]) -> Tuple[int, int]:
        successes, errors = 0, 0
        for document in documents:
            if "id" in document:
                self.documents.append(document)
                successes += 1
            else:
                errors += 1
        return successes, errors

    async def update_document(self, datastore_name: str, document_id: str, document: Document) -> Tuple[bool, bool]:
        to_update = [d for d in self.documents if d["id"] == document_id]
        if to_update:
            self.documents.remove(to_update[0])
        self.documents.append(document)
        return (True, True)

    async def delete_document(self, datastore_name: str, document_id: str) -> bool:
        to_remove = [d for d in self.documents if d["id"] == document_id]
        if to_remove:
            self.documents.remove(to_remove[0])
            return True
        else:
            return False

    async def has_document(self, datastore_name: str, document_id: str) -> bool:
        return len([d for d in self.documents if d["id"] == document_id]) > 0

    # --- Search ---

    async def search(self, datastore_name: str, query: str, feedback_documents: List[str] = None, n_hits=10) -> List[QueryResult]:
        return [QueryResult(document=self.query_document, score=1.0, id='doc0')]

    async def search_for_id(self, datastore_name: str, query: str, document_id: str):
        to_retrieve = [d for d in self.documents if d["id"] == document_id]
        return QueryResult(document=to_retrieve[0], score=1.0, id='doc0') if to_retrieve else None

    # --- Management methods ---

    async def commit_changes(self):
        pass
