from typing import List

from fastapi import APIRouter, Response
from fastapi.param_functions import Body, Path, Query
from fastapi.responses import JSONResponse, StreamingResponse

from ..core.db import db
from ..core.generate_package import generate_and_upload_package
from ..core.vespa_app import vespa_app
from ..models.index import Index, IndexRequest, create_index_object


router = APIRouter(tags=["Indices"])


@router.put("/datastore/{datastore_name}/indices/{index_name}")
async def put_index(
    datastore_name: str = Path(...), index_name: str = Path(...), index_request: IndexRequest = Body(...)
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        new_index = create_index_object(datastore_name, index_name, index_request)
        success = await db.add_index(new_index) is not None
    else:
        new_index = create_index_object(datastore_name, index_name, index_request)
        success = await db.update_index(new_index)

    if success:
        success_upload = await generate_and_upload_package()
        if success_upload:
            return new_index
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=400)


@router.get("/datastore/{datastore_name}/indices/{index_name}/status")
async def get_index_status(datastore_name: str = Path(...), index_name: str = Path(...)):
    # TODO
    pass


def retrieve_document_embeddings(datastore_name: str, index_name: str):
    endpoint = "{0}/document/v1/{1}/{1}/docid".format(vespa_app.end_point, datastore_name)
    response = vespa_app.http_session.get(endpoint, cert=vespa_app.cert).json()
    for document in response["documents"]:
        if index_name in document["fields"]:
            yield "{}, {}".format(
                document["id"], [x["value"] for x in document["fields"][index_name]["cells"]]
            ).encode()
    continuation = response.get("continuation", None)
    while continuation is not None:
        vespa_format = {
            "continuation": continuation,
        }
        response = vespa_app.http_session.get(endpoint, params=vespa_format, cert=vespa_app.cert).json()
        for document in response["documents"]:
            if index_name in document["fields"]:
                yield "{}, {}".format(
                    document["id"], [x["value"] for x in document["fields"][index_name]["cells"]]
                ).encode()
        continuation = response.get("continuation", None)


# TODO currently not working
@router.get("/datastore/{datastore_name}/indices/{index_name}/embeddings")
async def get_index_embeddings(datastore_name: str = Path(...), index_name: str = Path(...)):
    return StreamingResponse(
        retrieve_document_embeddings(datastore_name, index_name), media_type="application/octet-stream"
    )


@router.delete("/datastore/{datastore_name}/indices/{index_name}")
async def delete_index(datastore_name: str = Path(...), index_name: str = Path(...)):
    success = await db.delete_index(datastore_name, index_name)
    if success:
        success &= await generate_and_upload_package(allow_content_removal=True)
        if success:
            return Response(status_code=204)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=400)


@router.get("/datastore/{datastore_name}/indices/{index_name}/embeddings/{doc_id}")
async def get_document_embedding(
    datastore_name: str = Path(...), index_name: str = Path(...), doc_id: str = Path(...)
):
    res = vespa_app.get_data(datastore_name, doc_id)
    doc = res.json
    embedding_name = Index.get_embedding_field_name(index_name)
    if res.status_code == 200 and embedding_name in doc["fields"]:
        return [x["value"] for x in doc["fields"][embedding_name]["cells"]]
    return Response(status_code=404)


@router.post("/datastore/{datastore_name}/indices/{index_name}/embeddings/{doc_id}")
async def set_document_embedding(
    datastore_name: str = Path(...),
    index_name: str = Path(...),
    doc_id: str = Path(...),
    embedding: List[float] = Body(...),
):
    embedding_name = Index.get_embedding_field_name(index_name)
    fields = {embedding_name: {"values": embedding}}
    response = vespa_app.update_data(datastore_name, doc_id, fields)
    return JSONResponse(status_code=response.status_code, content=response.json)


# TODO
# @router.post("/datastore/{datastore_name}/indices/{index_name}/indexing")
# async def update_index(
#     datastore_name: str = Path(...), index_name: str = Path(...), reindex: str = Path(...), filtering: list = Body([])
# ):
#     pass


@router.get("/datastore/{datastore_name}/indices")
async def get_all_indices(datastore_name: str = Path(...)):
    indices = await db.get_indices(datastore_name)
    return indices
