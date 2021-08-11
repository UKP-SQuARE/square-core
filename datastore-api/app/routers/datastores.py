from typing import List

from fastapi import APIRouter, Response, status
from fastapi.param_functions import Query
from vespa.package import Document, FieldSet, Schema

from ..core.db import db
from ..core.generate_package import generate_and_upload_package
from ..models.datastore import Datastore, DatastoreField, DatastoreResponse


router = APIRouter(tags=["Datastores"])


@router.get("", response_model=List[DatastoreResponse])
async def get_all_datastores(
    limit: int = Query(200, description="Maximal number of datastores to retrieve.")
):
    schemas = await db.get_schemas(limit=limit)
    return [Datastore.from_vespa(schema) for schema in schemas]


@router.get("/{datastore_name}", response_model=DatastoreResponse)
async def get_datastore(datastore_name: str):
    schema = await db.get_schema(datastore_name)
    if schema is None:
        return Response(status_code=404)
    return Datastore.from_vespa(schema)


@router.put("/{datastore_name}", response_model=DatastoreResponse)
async def put_datastore(datastore_name: str, fields: List[DatastoreField], response: Response):
    # Update if existing, otherwise add new
    schema = await db.get_schema(datastore_name)
    success = False
    if schema is None:
        schema = Schema(datastore_name, Document(), fieldsets=[FieldSet("default", [f.name for f in fields if f.use_for_ranking])])
        schema.add_fields(*[field.to_vespa() for field in fields])
        success = await db.add_schema(schema) is not None
        response.status_code = status.HTTP_201_CREATED
    else:
        schema.add_fields(*[field.to_vespa() for field in fields])
        schema.fieldsets["default"].fields += [field.name for field in fields]
        success = await db.update_schema(schema)
        response.status_code = status.HTTP_200_OK

    if success:
        success_upload = await generate_and_upload_package()
        if success_upload:
            return Datastore.from_vespa(schema)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=400)


@router.delete("/{datastore_name}")
async def delete_datastore(datastore_name: str):
    success = await db.delete_schema(datastore_name)
    if success:
        success_upload = await generate_and_upload_package(allow_content_removal=True)
        if success_upload:
            return Response(status_code=204)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=404)
