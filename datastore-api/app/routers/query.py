from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.param_functions import Body, Path, Query

from ..models.httperror import HTTPError
from ..models.query import QueryResult
from .dependencies import get_search_client, get_storage_connector, client_credentials

router = APIRouter(tags=["Query"])


@router.get(
    "/search",
    summary="Search the documentstore with given query and return top-k documents",
    description="Searches the given datastore with the search strategy specified by the given index \
            and if necessery encodes the query with the specified encoder",
    response_description="The top-K documents",
    response_model=List[QueryResult],
    responses={
        200: {"model": List[QueryResult], "description": "The top-K documents"},
        404: {"model": HTTPError, "description": "The datastore or index does not exist"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def search(
    datastore_name: str = Path(..., description="Name of the datastore."),
    index_name: Optional[str] = Query(None, description="Index name."),
    query: str = Query(..., description="The query string."),
    top_k: int = Query(40, description="Number of documents to retrieve."),
    conn=Depends(get_storage_connector),
    dense_retrieval=Depends(get_search_client),
    credential_token=Depends(client_credentials)
):
    # do dense retrieval
    if index_name:
        try:
            return await dense_retrieval.search(
                datastore_name, 
                index_name, 
                query, 
                top_k,
                credential_token
            )
        except ValueError as ex:
            raise HTTPException(status_code=404, detail=str(ex))
        except Exception as other_ex:
            raise HTTPException(status_code=500, detail=str(other_ex))
    # do sparse retrieval
    else:
        return await conn.search(datastore_name, query, n_hits=top_k)


@router.post(
    "/search_by_vector",
    summary="Search a datastore with the given query vector and return top-k documents",
    description="Searches the given datastore with the search strategy specified by the given index",
    response_description="The top-K documents",
    response_model=List[QueryResult],
    responses={
        200: {"model": List[QueryResult], "description": "The top-K documents"},
        404: {"model": HTTPError, "description": "The datastore or index does not exist"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def search_by_vector(
    datastore_name: str = Path(..., description="Name of the datastore."),
    index_name: str = Body(..., description="Index name."),
    query_vector: List[float] = Body(..., description="Query vector."),
    top_k: int = Body(40, description="Number of documents to retrieve."),
    conn=Depends(get_storage_connector),
    dense_retrieval=Depends(get_search_client),
):
    # do dense retrieval
    try:
        return await dense_retrieval.search_by_vector(datastore_name, index_name, query_vector, top_k)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as other_ex:
        raise HTTPException(status_code=500, detail=str(other_ex))


@router.get(
    "/score",
    summary="Score the document with given query",
    description="Scores the document with the given id and the given query and returns the score.",
    response_description="The score",
    # response_model=QueryResultDocument,  # TODO
    responses={
        200: {
            "model": QueryResult,
            "description": "The score between the query and the documnt wiith the given id",
        },
        404: {"model": HTTPError, "description": "The datastore or index does not exist"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def score(
    datastore_name: str = Path(..., description="Name of the datastore."),
    index_name: Optional[str] = Query(None, description="Index name."),
    query: str = Query(..., description="The query string."),
    doc_id: str = Query(..., description="Document ID to retrieve."),
    conn=Depends(get_storage_connector),
    dense_retrieval=Depends(get_search_client),
    credential_token=Depends(client_credentials)
):
    # do dense retrieval
    if index_name:
        try:
            result = await dense_retrieval.score(
                datastore_name, 
                index_name, 
                query, 
                doc_id, 
                credential_token
            )
        except ValueError as ex:
            raise HTTPException(status_code=404, detail=str(ex))
        except Exception as other_ex:
            raise HTTPException(status_code=500, detail=str(other_ex))
    # do sparse retrieval
    else:
        result = await conn.search_for_id(datastore_name, query, doc_id)

    if not result:
        raise HTTPException(status_code=404, detail="Document not found.")
    return result
