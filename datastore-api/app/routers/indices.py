import logging
from typing import List

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.param_functions import Body, Path

from ..core.config import settings
from ..models.embedding import DocumentEmbedding
from ..models.httperror import HTTPError
from ..models.index import Index, IndexRequest
from .dependencies import get_search_client, get_storage_connector


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Indices"])


@router.get(
    "",
    summary="Lists all indices of a datastore",
    description="Returns a list of all indices in a datastore.",
    responses={
        200: {
            "description": "List of all indices found",
            "model": List[Index],
        }
    },
)
async def get_all_indices(
    datastore_name: str = Path(..., description="Datastore name"),
    conn=Depends(get_storage_connector),
):
    indices = await conn.get_indices(datastore_name)
    return indices


@router.get(
    "/{index_name}",
    summary="Get an index by its name",
    description="Returns an index for a datastore given its name.",
    responses={
        200: {"model": Index, "description": "The requested index"},
        404: {
            "description": "The requested index does not exist",
            "model": HTTPError,
        },
    },
)
async def get_index(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    conn=Depends(get_storage_connector),
):
    index = await conn.get_index(datastore_name, index_name)
    if index is None:
        raise HTTPException(status_code=404, detail="Index not found.")
    else:
        return index


@router.put(
    "/{index_name}",
    summary="Creates a new index or updates it if it exists",
    description="Creates a new index in  the specified datastore of a index with that name allready exists it is updated to the given configuration",
    responses={
        200: {"model": Index, "description": "The configuration of the updated index"},
        201: {"model": Index, "description": "The configuration of the created index"},
        400: {"model": HTTPError, "description": "The creation of the index failed in the API database"},
        500: {"model": HTTPError, "description": "The update of the index failed in VESPA"},
    },
)
async def put_index(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    index_request: IndexRequest = Body(..., description="The index configuration as IndexRequest"),
    conn=Depends(get_storage_connector),
    response: Response = None,
):
    index = await conn.get_index(datastore_name, index_name)
    if index is None:
        new_index = index_request.to_index(datastore_name, index_name)
        success = await conn.add_index(new_index) is not None
        response.status_code = status.HTTP_201_CREATED
    else:
        new_index = index_request.to_index(datastore_name, index_name)
        success = await conn.update_index(new_index)
        response.status_code = status.HTTP_200_OK

    if success:
        await conn.commit_changes()
        return new_index
    else:
        raise HTTPException(status_code=400)


@router.get("/{index_name}/status")
async def get_index_status(
    datastore_name: str = Path(...),
    index_name: str = Path(...),
    conn=Depends(get_storage_connector),
):
    index = await conn.get_index(datastore_name, index_name)
    status = {"bm25": index.bm25}
    yql = "select * from sources {} where  id > 0;".format(datastore_name)
    request = requests.get(settings.VESPA_APP_URL + "/search/", params={"yql": yql})
    if requests.status_codes == 404:
        raise HTTPException(status_code=404, detail="Could not get index status")
    status["total"] = request.json()["root"]["fields"]["totalCount"]

    if not status["bm25"]:
        pass
        # TODO Get number of documents with embedding
    return status


@router.delete(
    "/{index_name}",
    summary="Delete an index",
    description="Deletes the index with the corresponding name and all embeddings contained in the index",
    responses={
        204: {"description": "Successfully deleted index"},
        404: {"model": HTTPError, "description": "Failed to delete index in API database"},
        500: {"model": HTTPError, "description": "Failed to delete index in the storage backend."},
    },
)
async def delete_index(
    datastore_name: str = Path(..., description="The name of the datastore"),
    index_name: str = Path(..., description="The name of the index"),
    conn=Depends(get_storage_connector),
):
    success = await conn.delete_index(datastore_name, index_name)

    if success:
        await conn.commit_changes()
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)


@router.get(
    "/{index_name}/embeddings/{doc_id}",
    summary="Get embedding for a document",
    description="Returns the embedding for a document in the indexwith the given id",
    responses={
        200: {"model": DocumentEmbedding, "description": "The embedding for the document with the given id"},
        404: {"model": HTTPError, "description": "Failed to find embedding for document with given id"},
    },
    response_model=DocumentEmbedding,
)
async def get_document_embedding(
    datastore_name: str = Path(..., description="The name of the datastore"),
    index_name: str = Path(..., description="The name of the index"),
    doc_id: str = Path(..., description="The id of the document"),
    dense_retrieval=Depends(get_search_client),
):
    try:
        embedding = await dense_retrieval.get_document_embedding(datastore_name, index_name, doc_id)
        return DocumentEmbedding(id=doc_id, embedding=embedding)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


# TODO
# @router.post("/{index_name}/indexing")
# async def update_index(
#     datastore_name: str = Path(...), index_name: str = Path(...), reindex: str = Path(...), filtering: list = Body([])
# ):
#     pass
