import json
import logging
from typing import Iterable, List, Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request, File, UploadFile
from fastapi.param_functions import Body, Path

from ..core.config import settings
from ..models.document import Document
from ..models.datastore import Datastore, DatastoreRequest
from ..models.stats import DatastoreStats
from ..models.httperror import HTTPError
from ..models.upload import UploadResponse, UploadUrlSet
from .dependencies import get_storage_connector, get_kg_storage_connector, get_mongo_client
from ..core.mongo import MongoClient

from ..core.kgs.connector import KnowledgeGraphConnector
from ..routers.documents import upload_document_file

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


@router.get(
    "/{kg_name}",
    summary="Get a knowledge graph",
    description="Get a knowledge graph by its name from the datastore API",
    responses={
        200: {
            "model": Datastore,
            "description": "The knowledge graph information",
        }
    },
    response_model=Datastore,
)
async def get_kg(
    kg_name: str = Path(..., description="The knowledge graph name"),
    conn=Depends(get_kg_storage_connector),
):
    schema = await conn.get_kg(kg_name)
    if schema is None:
        return Response(status_code=404)
    return schema


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
    schema = await conn.get_datastore(kg_name)
    success = False
    if schema is None:
        # creating a new datastore
        schema = fields.to_datastore(kg_name)
        success = await conn.add_datastore(schema)
        response.status_code = status.HTTP_201_CREATED
        if success:
            await mongo.new_binding(request, kg_name, binding_item_type)  # It should be placed after conn.add_datastore to make sure the status consistent between conn.add_datastore and mongo.new_binding
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


@router.delete(
    "/{kg_name}",
    summary="Delete a knowledge graph",
    description="Delete a knowledge graph from the datastore API",
    responses={
        204: {
            "description": "The knowledge graph is deleted",
        },
        404: {"description": "The knowledge graph could not be deleted from the API database"},
        500: {
            "description": "Failed to delete the knowledge graph from the storage backend.",
        },
    },
)
async def delete_kg(
    request: Request,
    kg_name: str = Path(..., description="The knowledge graph name"),
    conn: KnowledgeGraphConnector = Depends(get_kg_storage_connector),
    mongo: MongoClient = Depends(get_mongo_client)
):
    if not (await conn.get_kg(kg_name)):
        return Response(status_code=404)
    
    await mongo.autonomous_access_checking(request, kg_name, binding_item_type)
    success = await conn.delete_kg(kg_name)

    if success:    
        await mongo.delete_binding(request, kg_name, binding_item_type)
        await conn.commit_changes()
        return Response(status_code=204)
    else:
        return Response(status_code=404)


@router.get(
    "/{kg_name}/stats",
    summary="Get knowledge graph statistics",
    description="Get statistics such as document count and storage size in bytes for a knowledge graph.",
    responses={
        200: {
            "model": DatastoreStats,
            "description": "The knowledge graph statistics",
        },
        404: {"description": "The knowledge graph could not be found"},
    },
    response_model=DatastoreStats,
)
async def get_kg_stats(
    kg_name: str = Path(..., description="The knowledge graph name"),
    conn=Depends(get_kg_storage_connector),
):
    stats = await conn.get_kg_stats(kg_name)
    if stats is not None:
        return stats
    else:
        raise HTTPException(status_code=404)

@router.get(
    "/{kg_name}/relations",
    summary="Get all knowledge graph relations",
    description="Get all relations of a given knowledge graph.",
    responses={
        200: {
            #"model": List[Dict[str,int]],
            "description": "The knowledge graph relations",
        },
        404: {"description": "The knowledge graph relations could not be found"},
    },
    #response_model=List[Dict[str,int]],
)
async def get_kg_relations(
    kg_name: str = Path(..., description="The knowledge graph name"),
    conn=Depends(get_kg_storage_connector),
):
    stats = await conn.get_all_relations(kg_name)
    if stats is not None:
        return stats
    else:
        raise HTTPException(status_code=404)

###    Queries    ###
@router.put(
    "/{kg_name}/nodes/{node_id}",
    summary="Insert/Update a node.",
    description="Inserts/Updates a node with its ID as <node_id>.",
    responses={
        200: {"description": "The node has been succesfully updated."},
        400: {"description": "Failed to update the node in the API database"},
        500: {"description": "Failed to create the node in the storage backend."},
    },
)
async def put_node(
    request: Request,
    kg_name: str = Path(..., description="The knowledge graph name"),
    node_id: str = Path(..., description="The node name"),
    node: Document = Body(..., description="The node to upsert"),
    conn: KnowledgeGraphConnector = Depends(get_kg_storage_connector),
    mongo: MongoClient = Depends(get_mongo_client)
):
    kg = await conn.get_kg(kg_name)
    if kg is None:
        raise HTTPException(status_code=404, detail="KG not found.")

    await mongo.autonomous_access_checking(request, kg_name, binding_item_type)

    # First, check if all fields in the uploaded node are valid.
    if not kg.is_valid_document(node):
        raise HTTPException(
            status_code=400,
            detail="The given document does not have the correct format.",
        )
    # also check if the node id in the body matches the one in the path
    if node_id != node.id:
        raise HTTPException(
            status_code=400,
            detail="The node ID specified in the path and in the request body must match.",
        )

    success, created = await conn.add_document(datastore_name=kg_name, document_id=node_id, document=node)
    if success:
        if not created:
            status_code = 200
        else:
            status_code = 201
        return Response(
            status_code=status_code,
            headers={"Location": request.url_for("get_object_by_id", kg_name=kg_name, object_id=node_id)},
        )
    else:
        raise HTTPException(status_code=500)

@router.post(
    "/{kg_name}/nodes",
    summary="Upload a batch of nodes",
    response_model=UploadResponse,
    status_code=201,
    responses={
        200: {"description": "Number of successfully uploaded nodes to the knowledge graph."},
        400: {"model": UploadResponse, "description": "Error during Upload"},
        404: {"model": HTTPError, "description": "The knowledge graph does not exist."},
        422: {"description": "Cannot instantiate a Document object"}
    },
)
async def post_kg_nodes(
    request: Request,
    kg_name: str = Path(..., description="The name of the knowledge graph"),
    documents: List[Document] = Body(..., description="Batch of documents to be uploaded."),
    conn = Depends(get_kg_storage_connector),
    response: Response = None,
    mongo: MongoClient = Depends(get_mongo_client)
):
    kg = await conn.get_kg(kg_name)
    if kg is None:
        raise HTTPException(status_code=404, detail="Knowledge graph not found.")

    await mongo.autonomous_access_checking(request, kg_name, binding_item_type)

    successes, errors = await conn.add_document_batch(kg_name, documents)
    if errors > 0:
        response.status_code = 400
        return UploadResponse(
            message=f"Unable to upload {errors} documents.", successful_uploads=successes, errors=errors
        )
    else:
        return UploadResponse(message=f"Successfully uploaded {successes} documents.", successful_uploads=successes)


###    QUERIES    ###
@router.post(
    "/{kg_name}/nodes/query_by_name",
    summary="Get a node from a knowledge graph",
    description="Get a node from the knowledge graph by name",
    responses={
        200: {
            "description": "The node",
            #"model": Document,
        },
        404: {"description": "The nodes could not be retrieved"},
    },
)
async def get_node_by_name(
    kg_name: str = Path(..., description="The name of the node"),
    doc_id: set = Body(..., description="The name of the node to retrieve"),
    conn=Depends(get_kg_storage_connector),
):
    result = await conn.get_node_by_name_msearch(kg_name, doc_id)
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find node.")


@router.get(
    "/{kg_name}/nodes/query_nodes_inbetween",
    summary="Get a list of nodes which are between a pair of nodes.",
    description="Returns a list of nodes, which are inbetween a list of node-pairs..",
    responses={
        200: {
            "description": "List of nodes",
        },
        404: {"description": "The edges could not be retrieved"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def get_edges_by_id_as_nodes(
    kg_name: str = Path(..., description="The name of the edge"),
    nids_pair: List = Body(..., description="The name of the edge to retrieve"),
    conn=Depends(get_kg_storage_connector),
):
    #  Changee description!!
    result = await conn.get_nodes_for_nodepairs(kg_name, nids_pair)
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find edge.")

@router.post(
    "/{kg_name}/subgraph/query_by_node_name",
    summary="summary",
    description="Get the subgraph of a given List of node-names and the number of hops",
    responses={
        200: {
            #"model": DatastoreStats,
            "description": "The subgraph as a set of nodes and edges",
        },
        404: {"description": "The subgraph could not be retrieved"},
    },
    #response_model=DatastoreStats,
)
async def subgraph_by_names(
    kg_name: str = Path(..., description="The knowledge graph name"),
    nids: set = Body(..., description="List of node names."),
    hops: int = Body(2, description="Number of hops to retrieve."),
    conn=Depends(get_kg_storage_connector),
):
    # Need to handle if wrong kg_name was gave as an input
    subgraph = await conn.extract_subgraph_by_names(kg_name, nodes=nids, hops=hops)
    if subgraph is not None:
        return subgraph
    else:
        raise HTTPException(status_code=404)
        

@router.post(
    "/{kg_name}/subgraph/query_by_node_id",
    summary="summary",
    description="Get the subgraph of a given List of node-ids and the number of hops",
    responses={
        200: {
            #"model": DatastoreStats,
            "description": "The subgraph as a set of nodes and edges",
        },
        404: {"description": "The subgraph could not be retrieved"},
    },
    #response_model=DatastoreStats,
)
async def subgraph_by_ids(
    kg_name: str = Path(..., description="The knowledge graph name"),
    nids: set = Body(..., description="List of node ids."),
    hops: int = Body(2, description="Number of hops to retrieve."),
    conn=Depends(get_kg_storage_connector),
):
    # Need to handle if wrong kg_name was gave as an input
    subgraph = await conn.extract_subgraph_by_ids(kg_name, nodes=nids, hops=hops)
    if subgraph is not None:
        return subgraph
    else:
        raise HTTPException(status_code=404)

@router.get(
    "/{kg_name}/edges/query_by_ids",
    summary="Get edges between given node_ids",
    description="Get edges between node_pairs for a given list of node_id_pairs from the knowledge.",
    responses={
        200: {
            "description": "The nodes",
        },
        404: {"description": "The nodes could not be retrieved"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def get_edges_by_nids(
    kg_name: str = Path(..., description="The name of the knowledge graph"),
    nids: List[set] = Body(..., description="List of node_id-pairs"),
    conn=Depends(get_kg_storage_connector),
): 
    result = await conn.get_edge_msearch(kg_name, nids)
    
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find nodes.")

@router.get(
    "/{kg_name}/edges/query_relationinfo",
    summary="Get the relation info between given node_ids",
    description="Get relation info between node_pairs for a given list of node_id_pairs from the knowledge.",
    responses={
        200: {
            "description": "The nodes",
        },
        404: {"description": "The nodes could not be retrieved"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def get_relationinfo(
    kg_name: str = Path(..., description="The name of the knowledge graph"),
    nids: List[set] = Body(..., description="List of node_id-pairs"),
    conn=Depends(get_kg_storage_connector),
): 
    result = await conn.get_relation(kg_name, nids)
    
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find nodes.")    

@router.post(
    "/{kg_name}/edges/query_by_name",
    summary="Get a edge from a knowledge graph",
    description="Get a edge from the knowledge graph by name",
    responses={
        200: {
            "description": "The edge",
        },
        404: {"description": "The edge could not be retrieved"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def get_edge_by_name(
    kg_name: str = Path(..., description="The name of the knowledge graph"),
    docid: List = Body(..., description="The name of the edge to retrieve"),
    conn=Depends(get_kg_storage_connector),
):
    result = await conn.edges_in_out_msearch(kg_name, docid)
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find edge.")

@router.get(
    "/{kg_name}/edges/query_by_id_as_nodes",
    summary="Get list of nodes which go in or out of given node for given knowledge graph",
    description="Returns a list of nodes, which either go in or out of the given node.",
    responses={
        200: {
            "description": "List of nodes",
        },
        404: {"description": "The edges could not be retrieved"},
        500: {"model": HTTPError, "description": "Model API error"},
    },
)
async def get_edges_by_id_as_nodes(
    kg_name: str = Path(..., description="The name of the edge"),
    docid: List = Body(..., description="The name of the edge to retrieve"),
    conn=Depends(get_kg_storage_connector),
):
    result = await conn.extract_nodes(kg_name, docid)
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find edge.")

@router.get(
    "/{kg_name}/{object_id}",
    summary="Get a node/edge from a knowledge graph",
    description="Get a node/edge from the knowledge graph by its ID.",
    responses={
        200: {
            "description": "The node/edge",
            "model": Document,
        },
        400: {"model": HTTPError, "description": "Failed to retrieve node"},
    },
)
async def get_object_by_id(
    kg_name: str = Path(..., description="The name of the knowdledge graph"),
    object_id: str = Path(..., description="The name of the node/edge to retrieve"),
    conn=Depends(get_kg_storage_connector),
):
    result = await conn.get_object_by_id_msearch(kg_name, [object_id])
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find node/edge.")


@router.delete(
    "/{kg_name}/{object_id}",
    summary="Delete a node/edge from knwoledge graph",
    description="Delete a node/edge from the datastore API by its ID.",
    responses={
        204: {
            "description": "The node/edge is deleted",
        },
        404: {"description": "The node/edge could not be deleted from the API database"},
        500: {
            "description": "Failed to delete the node/edge from the storage backend.",
        },
    },
)
async def delete_object(
    request: Request,
    kg_name: str = Path(..., description="The knowledge graph name"),
    object_id: str = Path(..., description="The node/edge ID"),
    conn: KnowledgeGraphConnector = Depends(get_kg_storage_connector),
    mongo: MongoClient = Depends(get_mongo_client)
):
    if not (await conn.get_object_by_id_msearch(kg_name, [object_id])):
        return Response(status_code=404)
    
    await mongo.autonomous_access_checking(request, kg_name, binding_item_type)
    success = await conn.delete_document(kg_name, object_id)
    if success:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find document to delete.")
