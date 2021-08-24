from typing import List

from fastapi import APIRouter, Response, status
from fastapi.param_functions import Body, Path, Query

from ..core.db import db
from ..core.generate_package import package_generator
from ..models.datastore import DatastoreRequest, DatastoreResponse


router = APIRouter(tags=["Datastores"])


@router.get(
    "",
    summary="Get all datastores",
    description="Get all datastores from the datastore API",
    responses={
        200: {
            "model": List[DatastoreResponse],
            "description": "List of all datastores",
        }
    },
    response_model=List[DatastoreResponse],
)
async def get_all_datastores(limit: int = Query(200, description="Maximal number of datastores to retrieve.")):
    schemas = await db.get_schemas(limit=limit)
    return [DatastoreResponse.from_vespa(schema) for schema in schemas]


@router.get(
    "/{datastore_name}",
    summary="Get a datastore",
    description="Get a datastore by its name from the datastore API",
    responses={
        200: {
            "model": DatastoreResponse,
            "description": "The datastore information",
        }
    },
    response_model=DatastoreResponse,
)
async def get_datastore(datastore_name: str = Path(..., description="The datastore name")):
    schema = await db.get_schema(datastore_name)
    if schema is None:
        return Response(status_code=404)
    return DatastoreResponse.from_vespa(schema)


@router.put(
    "/{datastore_name}",
    summary="Create a datastore",
    description="Create a new datastore",
    responses={
        200: {
            "model": DatastoreResponse,
            "description": "The datastore information",
        },
        400: {
            "description": "Failed to create the datastore in the API database",
        },
        500: {
            "description": "Failed to create the datastore in vespa",
        },
    },
    response_model=DatastoreResponse,
)
async def put_datastore(
    datastore_name: str = Path(..., description="The datastore name"),
    fields: DatastoreRequest = Body(..., description="The datastore fields"),
    response: Response = None,
):
    # Update if existing, otherwise add new
    schema = await db.get_schema(datastore_name)
    success = False
    if schema is None:
        schema = fields.to_vespa(datastore_name)
        success = await db.add_schema(schema) is not None
        response.status_code = status.HTTP_201_CREATED
    else:
        schema = fields.to_vespa(datastore_name)
        success = await db.update_schema(schema)
        response.status_code = status.HTTP_200_OK

    if success:
        success_upload = await package_generator.generate_and_upload()
        if success_upload:
            return DatastoreResponse.from_vespa(schema)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=400)


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
async def delete_datastore(datastore_name: str = Path(..., description="The datastore name")):
    success = await db.delete_schema(datastore_name)
    if success:
        success_upload = await package_generator.generate_and_upload(allow_content_removal=True)
        if success_upload:
            return Response(status_code=204)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=404)
