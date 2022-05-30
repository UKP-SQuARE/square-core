from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.param_functions import Body, Path

from ..models.datastore import Datastore, DatastoreRequest
from ..models.stats import DatastoreStats
from .dependencies import get_storage_connector, get_kg_storage_connector, get_mongo_client
from ..core.mongo import MongoClient

from ..core.kgs.connector import KnowledgeGraphConnector


router = APIRouter(tags=["Knowledge Graphs"])
binding_item_type = 'datastore'

@router.get(
    "",
    summary="Get all knowledge graphs",
    description="Get all knowledge graphs from the datastore API",
    responses={
        200: {
            "model": List[Datastore],
            "description": "List of all knowledge graphs",
        }
    },
    response_model=List[Datastore],
)
async def get_all_kgs(
    conn=Depends(get_kg_storage_connector),
):
    return await conn.get_kgs()

###  BUG: PUT-Request goes through and kgs are being created. But is still returning a 500 ERROR
@router.put(
    "/{kg_name}",
    summary="Create a knowledge graph",
    description="Create a new knowledge graph",
    responses={
        200: {
            "model": Datastore,
            "description": "The knowledge graph information",
        },
        400: {
            "description": "Failed to create the knowledge graph in the API database",
        },
        500: {
            "description": "Failed to create the knowledge graph in the storage backend.",
        },
    },
    response_model=Datastore,
)

async def put_kg(
    request: Request,
    kg_name: str = Path(..., description="The knowledge graph name"),
    fields: DatastoreRequest = Body(..., description="The knowledge graph fields"),
    conn: KnowledgeGraphConnector = Depends(get_kg_storage_connector),
    response: Response = None,
    mongo: MongoClient = Depends(get_mongo_client)
):
    # Update if existing, otherwise add new
    schema = await conn.add_kg(kg_name)
    success = False
    if schema is None:
        # creating a new datastore
        schema = fields.to_datastore(kg_name)
        success = await conn.add_kg(schema)
        response.status_code = status.HTTP_201_CREATED
        if success:
            await mongo.new_binding(request, kg_name, binding_item_type) 
    else:
        # updating an existing datastore
        await mongo.autonomous_access_checking(request, kg_name, binding_item_type)
        schema = fields.to_datastore(kg_name)
        success = await conn.update_datastore(schema)
        response.status_code = status.HTTP_200_OK

    if success:
        await conn.commit_changes()
        return schema
    else:
        raise HTTPException(status_code=400)