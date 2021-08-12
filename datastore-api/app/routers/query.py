from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Path, Query

from ..core.db import db
from ..core.model_api import encode_query
from ..core.utils import get_fields
from ..core.vespa_app import vespa_app
from ..models.index import Index
from ..models.query import QueryResult, QueryResultDocument


router = APIRouter(tags=["Query"])


@router.get(
    "/{index_name}/search",
    summary="Search the documentstore with given query and return top-k documents",
    description="Searches the given datastore with the search strategy specified by the given index \
            and if necessery encodes the query with the specified encoder",
    response_description="The top-K documents",
    response_model=QueryResult,
)
async def search(
    datastore_name: str = Path(..., description="Name of the datastore."),
    index_name: str = Path(..., description="Index name."),
    query: str = Query(..., description="The query string."),
    top_k: int = Query(40, description="Number of documents to retrieve."),
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        raise HTTPException(status_code=404, detail="Datastore or index not found.")
    try:
        query_embedding = encode_query(query, index)
    except Exception:
        raise HTTPException(status_code=500, detail="Model API error.")
    query_embedding_name = Index.get_query_embedding_field_name(index)
    body = {
        "query": query,
        "type": "any",
        "yql": f"select * from sources {datastore_name} where {index.yql_where_clause};",
        "ranking.profile": index_name,
        f"ranking.features.query({query_embedding_name})": query_embedding,
        "hits": top_k,
    }

    vespa_response = vespa_app.query(body=body)
    if vespa_response.status_code == 200:
        fields = await get_fields(datastore_name)
        return QueryResult.from_vespa(vespa_response.json, fields)
    else:
        raise HTTPException(status_code=500)


@router.get("/{index_name}/score", response_model=QueryResultDocument)
async def score(
    datastore_name: str = Path(..., description="Name of the datastore."),
    index_name: str = Path(..., description="Index name."),
    query: str = Query(..., description="The query string."),
    doc_id: int = Query(..., description="Document ID to retrieve."),
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        raise HTTPException(status_code=404, detail="Datastore or index not found.")
    try:
        query_embedding = encode_query(query, index)
    except Exception:
        raise HTTPException(status_code=500, detail="Model API error.")
    query_embedding_name = Index.get_query_embedding_field_name(index)
    body = {
        "query": query,
        "type": "any",
        # The only difference compared to the search is the additional filtering by doc_id
        "yql": f"select * from sources {datastore_name} where id={doc_id} and ({index.yql_where_clause});",
        "ranking.profile": index_name,
        f"ranking.features.query({query_embedding_name})": query_embedding,
    }

    vespa_response = vespa_app.query(body=body)
    if vespa_response.status_code == 200:
        fields = await get_fields(datastore_name)
        query_result = QueryResult.from_vespa(vespa_response.json, fields)
        # Extract first (and only) document from result if present, otherwise return 404
        if len(query_result.documents) > 0:
            return query_result.documents[0]
        else:
            raise HTTPException(status_code=404, detail="Document not found.")
    else:
        raise HTTPException(status_code=500)
