from fastapi import APIRouter, Response
from fastapi.param_functions import Path, Query

from ..core.db import db
from ..core.models import *
from ..core.vespa_app import vespa_app


router = APIRouter(tags=["Query"])


@router.get(
    "/datastore/{datastore_name}/indexs/{index_name}/search",
    summary="Search the documentstore with given query and return top-k documents",
    description="Searches the given datastore with the search strategy specified by the given index \
            and if necessery encodes the query with the specified encoder",
    response_description="The top-K documents",
)
async def search(
    datastore_name: str = Path(..., description="Name of the datastore."),
    index_name: str = Path(..., description="Index name."),
    query: str = Query(..., description="The query string."),
    top_k: int = Query(40, description="Number of documents to retrieve."),
    query_encoder: str = Query("dpr", description="Identifier of the query encoder."),
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        return Response(status_code=404, content="Datastore or index not found.")
    query_embedding = encode_query(query_encoder, query)
    body = {
        "query": query,
        "type": "any",
        "yql": index.query_yql,
        "ranking.profile": index_name,
        "ranking.features.query(query_embedding)": query_embedding,
        "hits": top_k,
    }
    result = vespa_app.query(
        body=body
    )
    return result.json
