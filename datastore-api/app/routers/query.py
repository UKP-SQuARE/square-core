from fastapi import APIRouter
from fastapi.param_functions import Path, Query
from fastapi.responses import PlainTextResponse

from ..core.db import db
from ..core.model_api import encode_query
from ..core.vespa_app import vespa_app
from ..models.index import Index


router = APIRouter(tags=["Query"])


@router.get(
    "/{index_name}/search",
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
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        return PlainTextResponse(status_code=404, content="Datastore or index not found.")
    try:
        query_embedding = encode_query(query, index)
    except Exception:
        return PlainTextResponse(status_code=500, content="Model API error.")
    query_embedding_name = Index.get_query_embedding_field_name(index)
    body = {
        "query": query,
        "type": "any",
        "yql": index.query_yql,
        "ranking.profile": index_name,
        f"ranking.features.query({query_embedding_name})": query_embedding,
        "hits": top_k,
    }
    result = vespa_app.query(
        body=body
    )
    return result.json
