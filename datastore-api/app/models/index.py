from typing import Any, Dict, Optional

from pydantic import BaseModel
from vespa.package import HNSW, Field, RankProfile, SecondPhaseRanking


class Index(BaseModel):
    """Models one index in a datastore."""

    datastore_name: str
    name: str
    query_yql: str

    # Model
    document_encoder: Optional[str]

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
    document_encoder: Optional[str] = None
    embedding_size: Optional[int] = None
    distance_metric: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "bm25": False,
                "document_encoder": "facebook/dpr-ctx_encoder-single-nq-base",
                "embedding_size": 769,
                "distance_metric": "euclidean",
            }
        }


def create_index_object(datastore_name: str, index_name: str, index_request: IndexRequest):
    if index_request.bm25:
        yql = "select * from sources {} where userQuery();".format(datastore_name)
        attributes = ["title", "text"]  # TODO
        ranking_expression = " + ".join(["bm25({})".format(a) for a in attributes])
        embedding_type = None
        hnsw = None
    else:
        embedding_name = Index.get_embedding_field_name(index_name)
        yql = "select * from sources " + datastore_name + " where ([{'targetNumHits':100, 'hnsw.exploreAdditionalHits':100}]nearestNeighbor(" + embedding_name + ",query_embedding)) or userQuery();"
        ranking_expression = "closeness({})".format(embedding_name)
        embedding_type = "tensor<float>(x[{}])".format(index_request.embedding_size)
        hnsw = {
            "distance_metric": index_request.distance_metric,
            "max_links_per_node": 16,
            "neighbors_to_explore_at_insert": 200,
        }
    return Index(
        datastore_name=datastore_name,
        name=index_name,
        query_yql=yql,
        document_encoder=index_request.document_encoder,
        embedding_type=embedding_type,
        hnsw=hnsw,
        first_phase_ranking=ranking_expression,
        second_phase_ranking=None,
    )
