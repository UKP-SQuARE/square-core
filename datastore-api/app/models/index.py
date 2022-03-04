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
    embedding_mode: Optional[str] = None  # pooling: cls, max, mean or pooler. This will not work for SBERT model type
    index_url: Optional[str] = None
    index_ids_url: Optional[str] = None
    index_description: Optional[str] = None
    collection_url: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "datastore_name": "wiki",
                "name": "dpr",
                "doc_encoder_model": "facebook/dpr-ctx_encoder-single-nq-base",
                "query_encoder_model": "facebook/dpr-question_encoder-single-nq-base",
                "embedding_size": 768,
                "embedding_mode": "pooler",
                "index_url": "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/dpr-single-nq-base.size-full/nq-QT_8bit_uniform-ivf262144.index",
                "index_ids_url": "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/dpr-single-nq-base.size-full/nq-QT_8bit_uniform-ivf262144.txt",
                "index_description": "It uses Faiss-IVF-SQ with nlist = 2^18, nprobe = 512 and 8bit uniform. For the indexing script, please refer to https://gist.github.com/kwang2049/d23550604059ed1576ac6cffb7e09fb2",
                "collection_url": "https://dl.fbaipublicfiles.com/dpr/wikipedia_split/psgs_w100.tsv.gz"
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
    embedding_mode: Optional[str] = None  # pooling: cls, max, mean or pooler. This will not work for SBERT model type
    index_url: Optional[str] = None
    index_ids_url: Optional[str] = None
    index_description: Optional[str] = None
    collection_url: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "doc_encoder_model": "facebook/dpr-ctx_encoder-single-nq-base",
                "query_encoder_model": "facebook/dpr-question_encoder-single-nq-base",
                "embedding_size": 768,
                "embedding_mode": "pooler",
                "index_url": "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/dpr-single-nq-base.size-full/nq-QT_8bit_uniform-ivf262144.index",
                "index_ids_url": "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/dpr-single-nq-base.size-full/nq-QT_8bit_uniform-ivf262144.txt",
                "index_description": "It uses Faiss-IVF-SQ with nlist = 2^18, nprobe = 512 and 8bit uniform. For the indexing script, please refer to https://gist.github.com/kwang2049/d23550604059ed1576ac6cffb7e09fb2",
                "collection_url": "https://dl.fbaipublicfiles.com/dpr/wikipedia_split/psgs_w100.tsv.gz"
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
