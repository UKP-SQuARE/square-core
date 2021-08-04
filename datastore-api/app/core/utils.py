from .db import db
from ..models.datastore import FIELDSET_NAME
from ..models.index import IndexRequest, Index
from vespa.package import QueryTypeField


async def get_fields(datastore_name: str):
    schema = await db.get_schema(datastore_name)
    fields = schema.fieldsets[FIELDSET_NAME].fields
    return fields


async def create_index_object(datastore_name: str, index_name: str, index_request: IndexRequest):
    if index_request.bm25:
        yql = "select * from sources {} where userQuery();".format(datastore_name)
        attributes = await get_fields(datastore_name)
        ranking_expression = " + ".join(["bm25({})".format(a) for a in attributes])
        embedding_type = None
        hnsw = None
    else:
        embedding_name = Index.get_embedding_field_name(index_name)
        query_embedding_name = Index.get_query_embedding_field_name(index_name)
        yql = (
            "select * from sources "
            + datastore_name
            + " where ([{'targetNumHits':100, 'hnsw.exploreAdditionalHits':100}]nearestNeighbor("
            + embedding_name
            + ","
            + query_embedding_name
            + ")) or userQuery();"
        )
        ranking_expression = "closeness({})".format(embedding_name)
        embedding_type = "tensor<float>(x[{}])".format(index_request.embedding_size)
        hnsw = {
            "distance_metric": index_request.distance_metric,
            "max_links_per_node": 16,
            "neighbors_to_explore_at_insert": 200,
        }
        # Every index that uses embeddings requires the type of the query embedding to be defined.
        query_type_field_name = f"ranking.features.query({query_embedding_name})"
        query_type_field_type = f"tensor<float>(x[{index_request.embedding_size}])"
        await db.add_query_type_field(QueryTypeField(query_type_field_name, query_type_field_type))

    return Index(
        datastore_name=datastore_name,
        name=index_name,
        query_yql=yql,
        doc_encoder_model=index_request.doc_encoder_model,
        doc_encoder_adapter=index_request.doc_encoder_adapter,
        query_encoder_model=index_request.query_encoder_model,
        query_encoder_adapter=index_request.query_encoder_adapter,
        embedding_type=embedding_type,
        hnsw=hnsw,
        first_phase_ranking=ranking_expression,
        second_phase_ranking=None,
    )
