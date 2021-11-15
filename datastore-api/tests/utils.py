import asyncio
import sys
from typing import Iterable, List, Optional, Tuple

from app.core.base_connector import BaseConnector
from app.models.datastore import Datastore
from app.models.document import Document
from app.models.index import Index
from app.models.query import QueryResult


def async_return(result):
    """
    Prepares the return value for mocked async functions.
    The default behavior for unittest.mock.patch() has changed for async functions in Python 3.8.
    """
    if sys.version_info >= (3, 8):
        return result
    else:
        f = asyncio.Future()
        f.set_result(result)
    return f


class MockConnector(BaseConnector):
    """Provides a mock datastore backend interface that keeps all data in local lists."""

    def __init__(self, datastores, indices, documents, query_document=None):
        super().__init__(None)
        self.datastores = datastores
        self.indices = indices
        self.documents = documents
        self.query_document = query_document

    async def get_datastores(self) -> List[Datastore]:
        return async_return(self.datastores)

    async def get_datastore(self, datastore_name: str) -> Optional[Datastore]:
        retrieved = [d for d in self.datastores if d.name == datastore_name]
        return async_return(retrieved[0] if retrieved else None)

    async def add_datastore(self, datastore: Datastore) -> bool:
        self.datastores.append(datastore)
        return async_return(True)

    async def update_datastore(self, datastore: Datastore) -> bool:
        to_update = [d for d in self.datastores if d.name == datastore.name]
        if to_update:
            self.datastores.remove(to_update[0])
        self.datastores.append(datastore)
        return async_return(True)

    async def delete_datastore(self, datastore_name: str) -> bool:
        to_remove = [d for d in self.datastores if d.name == datastore_name]
        if to_remove:
            self.datastores.remove(to_remove[0])
            return async_return(True)
        else:
            return async_return(False)

    # --- Index schemas ---

    async def get_indices(self, datastore_name: str) -> List[Index]:
        return async_return(self.indices)

    async def get_index(self, datastore_name: str, index_name: str) -> Optional[Index]:
        retrieved = [i for i in self.indices if i.name == index_name]
        return async_return(retrieved[0] if retrieved else None)

    async def add_index(self, index: Index) -> bool:
        self.indices.append(index)
        return async_return(True)

    async def update_index(self, index: Index) -> Tuple[bool, bool]:
        to_update = [i for i in self.indices if i.name == index.name]
        if to_update:
            self.indices.remove(to_update[0])
        self.indices.append(index)
        return async_return((True, True))

    async def delete_index(self, datastore_name: str, index_name: str) -> bool:
        to_remove = [i for i in self.indices if i.name == index_name]
        if to_remove:
            self.indices.remove(to_remove[0])
            return async_return(True)
        else:
            return async_return(False)

    # --- Documents ---

    async def get_documents(self, datastore_name: str) -> Iterable[Document]:
        for document in self.documents:
            yield async_return(document)

    async def get_document(self, datastore_name: str, document_id: int) -> Optional[Document]:
        retrieved = [d for d in self.documents if d["id"] == document_id]
        return async_return(retrieved[0] if retrieved else None)

    async def get_document_batch(self, datastore_name: str, document_ids: List[int]) -> List[Document]:
        return async_return([d for d in self.documents if d["id"] in document_ids])

    async def add_document(self, datastore_name: str, document_id: int, document: Document) -> Tuple[bool, bool]:
        self.documents.append(document)
        return async_return((True, True))

    async def add_document_batch(self, datastore_name: str, documents: Iterable[Document]) -> Tuple[int, int]:
        for document in documents:
            self.documents.append(document)
        return async_return((len(documents), 0))

    async def update_document(self, datastore_name: str, document_id: int, document: Document) -> Tuple[bool, bool]:
        to_update = [d for d in self.documents if d["id"] == document_id]
        if to_update:
            self.documents.remove(to_update[0])
        self.documents.append(document)
        return async_return((True, True))

    async def delete_document(self, datastore_name: str, document_id: int) -> bool:
        to_remove = [d for d in self.documents if d["id"] == document_id]
        if to_remove:
            self.documents.remove(to_remove[0])
            return async_return(True)
        else:
            return async_return(False)

    async def has_document(self, datastore_name: str, document_id: int) -> bool:
        return async_return(len([d for d in self.documents if d["id"] == document_id]) > 0)

    # --- Search ---

    async def search(self, datastore_name: str, query: str, n_hits=10) -> List[QueryResult]:
        return async_return([QueryResult(document=self.query_document, score=1.0)])

    async def search_for_id(self, datastore_name: str, query: str, document_id: int):
        to_retrieve = [d for d in self.documents if d["id"] == document_id]
        return async_return(QueryResult(document=to_retrieve[0], score=1.0) if to_retrieve else None)

    # --- Management methods ---

    async def commit_changes(self):
        pass
