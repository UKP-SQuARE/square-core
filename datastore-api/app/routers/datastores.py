from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.param_functions import Body, Path

from ..models.datastore import Datastore, DatastoreRequest
from ..models.stats import DatastoreStats
from .dependencies import get_storage_connector, get_mongo_client
from ..core.mongo import MongoClient
from ..core.es.connector import ElasticsearchConnector


router = APIRouter(tags=["Datastores"])
binding_item_type = 'datastore'

@router.get(
    "",
    summary="Get all datastores",
    description="Get all datastores from the datastore API",
    responses={
        200: {
            "model": List[Datastore],
            "description": "List of all datastores",
        }
    },
    response_model=List[Datastore],
)
async def get_all_datastores(
    conn=Depends(get_storage_connector),
):
    return await conn.get_datastores()


@router.get(
    "/{datastore_name}",
    summary="Get a datastore",
    description="Get a datastore by its name from the datastore API",
    responses={
        200: {
            "model": Datastore,
            "description": "The datastore information",
        }
    },
    response_model=Datastore,
)
async def get_datastore(
    datastore_name: str = Path(..., description="The datastore name"),
    conn=Depends(get_storage_connector),
):
    schema = await conn.get_datastore(datastore_name)
    if schema is None:
        return Response(status_code=404)
    return schema


@router.put(
    "/{datastore_name}",
    summary="Create a datastore",
    description="Create a new datastore",
    responses={
        200: {
            "model": Datastore,
            "description": "The datastore information",
        },
        400: {
            "description": "Failed to create the datastore in the API database",
        },
        500: {
            "description": "Failed to create the datastore in the storage backend.",
        },
    },
    response_model=Datastore,
)
async def put_datastore(
    request: Request,
    datastore_name: str = Path(..., description="The datastore name"),
    fields: DatastoreRequest = Body(..., description="The datastore fields"),
    conn: ElasticsearchConnector = Depends(get_storage_connector),
    response: Response = None,
    mongo: MongoClient = Depends(get_mongo_client)
):
    # Update if existing, otherwise add new
    schema = await conn.get_datastore(datastore_name)
    success = False
    if schema is None:
        # creating a new datastore
        schema = fields.to_datastore(datastore_name)
        success = await conn.add_datastore(schema)
        response.status_code = status.HTTP_201_CREATED
        if success:
            await mongo.new_binding(request, datastore_name, binding_item_type)  # It should be placed after conn.add_datastore to make sure the status consistent between conn.add_datastore and mongo.new_binding
    else:
        # updating an existing datastore
        await mongo.autonomous_access_checking(request, datastore_name, binding_item_type)
        schema = fields.to_datastore(datastore_name)
        success = await conn.update_datastore(schema)
        response.status_code = status.HTTP_200_OK

    if success:
        await conn.commit_changes()
        return schema
    else:
        raise HTTPException(status_code=400)


@router.delete(
    "/{datastore_name}",
    summary="Delete a datastore",
    description="Delete a datastore from the datastore API",
    responses={
        204: {
            "description": "The datastore is deleted",
        },
        404: {"description": "The datastore could not be deleted from the API database"},
        500: {
            "description": "Failed to delete the datastore from the storage backend.",
        },
    },
)
async def delete_datastore(
    request: Request,
    datastore_name: str = Path(..., description="The datastore name"),
    conn: ElasticsearchConnector = Depends(get_storage_connector),
    mongo: MongoClient = Depends(get_mongo_client)
):
    if not (await conn.get_datastore(datastore_name)):
        return Response(status_code=404)
    
    await mongo.autonomous_access_checking(request, datastore_name, binding_item_type)
    success = await conn.delete_datastore(datastore_name)

    if success:    
        await mongo.delete_binding(request, datastore_name, binding_item_type)
        await conn.commit_changes()
        return Response(status_code=204)
    else:
        return Response(status_code=404)


@router.get(
    "/{datastore_name}/stats",
    summary="Get datastore statistics",
    description="Get statistics such as document count and storage size in bytes for a datastore.",
    responses={
        200: {
            "model": DatastoreStats,
            "description": "The datastore statistics",
        },
        404: {"description": "The datastore could not be found"},
    },
    response_model=DatastoreStats,
)
async def get_datastore_stats(
    datastore_name: str = Path(..., description="The datastore name"),
    conn=Depends(get_storage_connector),
):
    stats = await conn.get_datastore_stats(datastore_name)
    if stats is not None:
        return stats
    else:
        raise HTTPException(status_code=404)
