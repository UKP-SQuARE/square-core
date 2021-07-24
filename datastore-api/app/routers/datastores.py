from fastapi import APIRouter, Response
from fastapi.param_functions import Query
from vespa.package import Schema, Document
from typing import List

from ..models.datastore import Datastore, DatastoreField
from ..core.db import db
from ..core.generate_package import generate_and_upload_package


router = APIRouter(tags=["Datastores"])


@router.get("/datastore/", response_model=List[Datastore])
async def get_all_datastores(
    limit: int = Query(200, description="Maximal number of datastores to retrieve.")
):
    schemas = await db.get_schemas(limit=limit)
    return [Datastore.from_vespa(schema) for schema in schemas]


@router.get("/datastore/{datastore_name}", response_model=Datastore)
async def get_datastore(datastore_name: str):
    schema = await db.get_schema(datastore_name)
    if schema is None:
        return Response(status_code=404)
    return Datastore.from_vespa(schema)


@router.put("/datastore/{datastore_name}", response_model=Datastore)
async def put_datastore(datastore_name: str, fields: List[DatastoreField]):
    # Update if existing, otherwise add new
    schema = await db.get_schema(datastore_name)
    success = False
    if schema is None:
        schema = Schema(datastore_name, Document())
        schema.add_fields(*[field.to_vespa() for field in fields])
        success = await db.add_schema(schema) is not None
    else:
        schema.add_fields(*[field.to_vespa() for field in fields])
        success = await db.update_schema(schema)

    if success:
        success_upload = await generate_and_upload_package()
        if success_upload:
            return Datastore.from_vespa(schema)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=400)


@router.delete("/datastore/{datastore_name}")
async def delete_datastore(datastore_name: str):
    success = await db.delete_schema(datastore_name)
    if success:
        success_upload = await generate_and_upload_package(allow_content_removal=True)
        if success_upload:
            return Response(status_code=204)
        else:
            return Response(status_code=400)
    else:
        return Response(status_code=404)
