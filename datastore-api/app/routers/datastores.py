from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.param_functions import Body, Path

from ..models.datastore import Datastore, DatastoreRequest
from .dependencies import get_storage_connector


router = APIRouter(tags=["Datastores"])


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
            "description": "Failed to create the datastore in vespa",
        },
    },
    response_model=Datastore,
)
async def put_datastore(
    datastore_name: str = Path(..., description="The datastore name"),
    fields: DatastoreRequest = Body(..., description="The datastore fields"),
    conn=Depends(get_storage_connector),
    response: Response = None,
):
    # Update if existing, otherwise add new
    schema = await conn.get_datastore(datastore_name)
    success = False
    if schema is None:
        schema = fields.to_datastore(datastore_name)
        success = await conn.add_datastore(schema)
        response.status_code = status.HTTP_201_CREATED
    else:
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
            "description": "Failed to delete the datastore from vespa",
        },
    },
)
async def delete_datastore(
    datastore_name: str = Path(..., description="The datastore name"),
    conn=Depends(get_storage_connector),
):
    success = await conn.delete_datastore(datastore_name)
    if success:
        conn.commit_changes()
        return Response(status_code=204)
    else:
        return Response(status_code=404)
