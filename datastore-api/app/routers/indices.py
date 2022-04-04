import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.param_functions import Body, Path

from ..models.embedding import DocumentEmbedding
from ..models.httperror import HTTPError
from ..models.index import Index, IndexRequest, IndexStatus
from .dependencies import get_search_client, get_storage_connector, client_credentials, get_mongo_client
from ..core.es.connector import ElasticsearchConnector
from ..core.mongo import MongoClient


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Indices"])
binding_item_type = 'index'


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
    request: Request,
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    index_request: IndexRequest = Body(..., description="The index configuration as IndexRequest"),
    conn: ElasticsearchConnector = Depends(get_storage_connector),
    response: Response = None,
    mongo: MongoClient = Depends(get_mongo_client)
):
    index = await conn.get_index(datastore_name, index_name)
    if index is None:
        # creating a new index
        new_index = index_request.to_index(datastore_name, index_name)
        success = await conn.add_index(new_index) is not None
        response.status_code = status.HTTP_201_CREATED
        if success:
            await mongo.new_binding(request, index_name, binding_item_type)  # It should be placed after conn.add_datastore to make sure the status consistent between conn.add_datastore and mongo.new_binding
    else:
        await mongo.autonomous_access_checking(request, index_name, binding_item_type)
        new_index = index_request.to_index(datastore_name, index_name)
        success = await conn.update_index(new_index)
        response.status_code = status.HTTP_200_OK

    if success:
        await conn.commit_changes()
        return new_index
    else:
        raise HTTPException(status_code=400)


@router.get(
    "/{index_name}/status",
    summary="Gets the status of an index",
    description="Returns whether an index is currently available for search.",
    responses={
        200: {"model": IndexStatus, "description": "Index status information."},
        404: {
            "description": "The requested index does not exist",
            "model": HTTPError,
        },
    },
)
async def get_index_status(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    conn=Depends(get_storage_connector),
    dense_retrieval=Depends(get_search_client),
    credential_token=Depends(client_credentials)
):
    index = await conn.get_index(datastore_name, index_name)
    if index is None:
        raise HTTPException(status_code=404, detail="Index not found.")
    else:
        is_available = await dense_retrieval.status(datastore_name, index_name, credential_token)
        return IndexStatus(is_available=is_available)


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
    request: Request,
    datastore_name: str = Path(..., description="The name of the datastore"),
    index_name: str = Path(..., description="The name of the index"),
    conn: ElasticsearchConnector = Depends(get_storage_connector),
    mongo: MongoClient = Depends(get_mongo_client)
):
    if not (await conn.get_index(datastore_name, index_name)):
        raise HTTPException(status_code=404)

    await mongo.autonomous_access_checking(request, index_name, binding_item_type)
    success = await conn.delete_index(datastore_name, index_name)

    if success:
        await mongo.delete_binding(request, index_name, binding_item_type)
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
