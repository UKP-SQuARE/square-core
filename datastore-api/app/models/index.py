from typing import Optional

from pydantic import BaseModel


class Index(BaseModel):
    """Models an index as stored in the database."""

    datastore_name: str
    name: str

    # Model
    doc_encoder_model: Optional[str] = None
    doc_encoder_adapter: Optional[str] = None
    query_encoder_model: Optional[str] = None
    query_encoder_adapter: Optional[str] = None
    embedding_size: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "datastore_name": "wiki",
                "name": "dpr",
                "doc_encoder_model": "facebook/dpr-ctx_encoder-single-nq-base",
                "query_encoder_model": "facebook/dpr-question_encoder-single-nq-base",
                "embedding_size": 768,
            }
        }

    @staticmethod
    def get_embedding_field_name(index) -> Optional[str]:
        if isinstance(index, str):
            return index + "_embedding"
        if index.embedding_type is not None:
            return index.name + "_embedding"
        else:
            return None

    @staticmethod
    def get_query_embedding_field_name(index) -> Optional[str]:
        if isinstance(index, str):
            return index + "_query_embedding"
        if index.embedding_type is not None:
            return index.name + "_query_embedding"
        else:
            return None


class IndexRequest(BaseModel):
    """Models an index as requested by the user."""

    doc_encoder_model: Optional[str] = None
    doc_encoder_adapter: Optional[str] = None
    query_encoder_model: Optional[str] = None
    query_encoder_adapter: Optional[str] = None
    embedding_size: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "doc_encoder_model": "facebook/dpr-ctx_encoder-single-nq-base",
                "query_encoder_model": "facebook/dpr-question_encoder-single-nq-base",
                "embedding_size": 768,
            }
        }

    def to_index(self, datastore_name, index_name):
        return Index(datastore_name=datastore_name, name=index_name, **self.dict())


class IndexStatus(BaseModel):
    """Models the status of an index."""

    is_available: bool

    class Config:
        schema_extra = {
            "example": {"is_available": True}
        }
