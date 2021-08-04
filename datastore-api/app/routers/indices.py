from io import BytesIO
from typing import List

import h5py
import requests
from fastapi import APIRouter, Response
from fastapi.param_functions import Body, Path, Query
from fastapi.responses import JSONResponse, StreamingResponse

from ..core.config import settings
from ..core.db import db
from ..core.generate_package import generate_and_upload_package
from ..core.utils import create_index_object
from ..core.vespa_app import vespa_app
from ..models.index import Index, IndexRequest
from ..models.upload import UploadResponse, UploadUrlSet


router = APIRouter(tags=["Indices"])


@router.put("/datastore/{datastore_name}/indices/{index_name}")
async def put_index(
    datastore_name: str = Path(...), index_name: str = Path(...), index_request: IndexRequest = Body(...)
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        new_index = await create_index_object(datastore_name, index_name, index_request)
        success = await db.add_index(new_index) is not None
    else:
        new_index = await create_index_object(datastore_name, index_name, index_request)
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


@router.get("/datastore/{datastore_name}/indices/{index_name}/embeddings", response_class=StreamingResponse)
async def get_document_embeddings(
    datastore_name: str = Path(...), index_name: str = Path(...),
    offset: int = Query(0), size: int = Query(100),
):
    if size > settings.MAX_RETURN_ITEMS:
        return Response(status_code=400, content="Size cannot be greater than {}".format(settings.MAX_RETURN_ITEMS))

    embedding_name = Index.get_embedding_field_name(index_name)
    batch = [(datastore_name, i) for i in range(offset, offset + size)]
    vespa_responses = vespa_app.get_batch(batch)

    buffer = BytesIO()
    with h5py.File(buffer, "w") as f:
        for response in vespa_responses:
            print(response.url)
            if response.status_code == 200 and embedding_name in response.json["fields"]:
                doc_id = response.json["id"].split(":")[-1]
                embedding = [x["value"] for x in response.json["fields"][embedding_name]["cells"]]
                f.create_dataset(doc_id, data=embedding)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/octet-stream")


@router.post(
    "/datastore/{datastore_name}/indices/{index_name}/embeddings",
    response_model=UploadResponse,
    status_code=201,
    responses={400: {"model": UploadResponse}},
)
def upload_document_embeddings_from_urls(
    datastore_name: str,
    index_name: str,
    urlset: UploadUrlSet,
    api_response: Response,
):
    doc_count = 0
    embedding_name = Index.get_embedding_field_name(index_name)

    for url in urlset.urls:
        r = requests.get(url)
        if r.status_code != 200:
            api_response.status_code = 400
            return UploadResponse(
                message=f"Failed to retrieve embeddings from {url}.",
                successful_uploads=doc_count,
            )
        # TODO how to handle files that are too big?
        buffer = BytesIO(r.content)
        with h5py.File(buffer, "r") as f:
            upload_batch = []
            for doc_id, embedding in f.items():
                fields = {embedding_name: {"values": embedding[:].tolist()}}
                upload_batch.append((datastore_name, doc_id, fields, False))
                doc_count += 1
                if doc_count % settings.VESPA_FEED_BATCH_SIZE == 0:
                    vespa_responses = vespa_app.update_batch(upload_batch)
                    for i, vespa_response in enumerate(vespa_responses):
                        print(vespa_response.json)
                        if vespa_response.status_code != 200:
                            api_response.status_code = 400
                            errored_doc_id = upload_batch[i][1]
                            return UploadResponse(
                                message=f"Unable to find document with id {errored_doc_id} in datastore.",
                                successful_uploads=doc_count,
                            )
                    upload_batch = []

    return UploadResponse(message=f"Successfully uploaded {doc_count} embeddings.", successful_uploads=doc_count)


@router.delete("/datastore/{datastore_name}/indices/{index_name}")
async def delete_index(datastore_name: str = Path(...), index_name: str = Path(...)):
    success = await db.delete_index(datastore_name, index_name)
    # also delete the corresponding query type field if available
    query_embedding_name = Index.get_query_embedding_field_name(index_name)
    query_type_field_name = f"ranking.features.query({query_embedding_name})"
    await db.delete_query_type_field(query_type_field_name)

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
    # TODO investigate, why create=False doesn't seem to work
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
