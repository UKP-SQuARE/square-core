from typing import Any, Dict, Optional

from pydantic import BaseModel
from vespa.package import HNSW, Field, RankProfile, SecondPhaseRanking


class Index(BaseModel):
    """Models one index in a datastore."""

    datastore_name: str
    name: str
    query_yql: str

    # Model
    doc_encoder_model: Optional[str]
    doc_encoder_adapter: Optional[str]
    query_encoder_model: Optional[str]
    query_encoder_adapter: Optional[str]

    # Embedding field
    embedding_type: Optional[str] = None
    hnsw: Optional[Dict[str, Any]] = None

    # Rank profile
    first_phase_ranking: str
    second_phase_ranking: Optional[str] = None

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

    def get_vespa_embedding_field(self) -> Optional[Field]:
        if self.embedding_type is not None:
            return Field(
                name=Index.get_embedding_field_name(self),
                type=self.embedding_type,
                indexing=["attribute", "index"],
                ann=HNSW.from_dict(self.hnsw) if self.hnsw is not None else None,
            )
        else:
            return None

    def get_vespa_rank_profile(self) -> RankProfile:
        return RankProfile(
            name=self.name,
            first_phase=self.first_phase_ranking,
            second_phase=SecondPhaseRanking(self.second_phase_ranking)
            if self.second_phase_ranking is not None
            else None,
            inherits="default",
        )


class IndexRequest(BaseModel):
    bm25: bool
    doc_encoder_model: Optional[str] = None
    doc_encoder_adapter: Optional[str] = None
    query_encoder_model: Optional[str] = None
    query_encoder_adapter: Optional[str] = None
    embedding_size: Optional[int] = None
    distance_metric: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "bm25": False,
                "doc_encoder_model": "facebook/dpr-ctx_encoder-single-nq-base",
                "query_encoder_model": "facebook/dpr-question_encoder-single-nq-base",
                "embedding_size": 769,
                "distance_metric": "euclidean",
            }
        }
