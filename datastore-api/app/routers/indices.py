import logging
from io import BytesIO
from typing import List, Union

import h5py
import numpy as np
import requests
from fastapi import APIRouter, HTTPException, Response, status, UploadFile, File
from fastapi.param_functions import Body, Path, Query
from fastapi.responses import JSONResponse, StreamingResponse

from ..core.config import settings
from ..core.db import db
from ..core.generate_package import package_generator
from ..core.utils import create_index_object
from ..core.vespa_app import vespa_app
from ..models.embedding import DocumentEmbedding
from ..models.index import Index, IndexRequest, IndexResponse
from ..models.upload import UploadResponse, UploadUrlSet


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Indices"])


@router.get("", response_model=List[IndexResponse])
async def get_all_indices(datastore_name: str = Path(...)):
    indices = await db.get_indices(datastore_name)
    return indices


@router.get("/{index_name}", response_model=IndexResponse)
async def get_index(datastore_name: str = Path(...), index_name: str = Path(...)):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        raise HTTPException(status_code=404, detail="Index not found.")
    else:
        return index


@router.put("/{index_name}", response_model=IndexResponse)
async def put_index(
    datastore_name: str = Path(...),
    index_name: str = Path(...),
    index_request: IndexRequest = Body(...),
    response: Response = None,
):
    index = await db.get_index(datastore_name, index_name)
    if index is None:
        new_index = await create_index_object(datastore_name, index_name, index_request)
        success = await db.add_index(new_index) is not None
        response.status_code = status.HTTP_201_CREATED
    else:
        new_index = await create_index_object(datastore_name, index_name, index_request)
        success = await db.update_index(new_index)
        response.status_code = status.HTTP_200_OK

    if success:
        success_upload = await package_generator.generate_and_upload()
        if success_upload:
            return new_index
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=400)


# TODO Implement index status method.
# @router.get("/{index_name}/status")
# async def get_index_status(datastore_name: str = Path(...), index_name: str = Path(...)):
#     pass


@router.get("/{index_name}/embeddings", response_class=StreamingResponse)
async def get_document_embeddings(
    datastore_name: str = Path(...),
    index_name: str = Path(...),
    offset: int = Query(0),
    size: int = Query(1000),
):
    if size > settings.MAX_RETURN_ITEMS:
        return HTTPException(
            status_code=400, detail="Size cannot be greater than {}".format(settings.MAX_RETURN_ITEMS)
        )

    embedding_name = Index.get_embedding_field_name(index_name)
    # TODO This assumes id is always numeric
    batch = [(datastore_name, i) for i in range(offset, offset + size)]
    vespa_responses = vespa_app.get_batch(batch)
    ids, embs = [], []
    for response in vespa_responses:
        if response.status_code == 200 and embedding_name in response.json["fields"]:
            doc_embedding = DocumentEmbedding.from_vespa(response.json, embedding_name)
            ids.append(doc_embedding.id)
            embs.append(doc_embedding.embedding)

    buffer = BytesIO()
    with h5py.File(buffer, "w") as f:
        f.create_dataset("ids", data=np.array(ids, dtype="S"), compression="gzip")
        f.create_dataset("embeddings", data=np.array(embs), compression="gzip")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/octet-stream")


def upload_embeddings_file(
    datastore_name: str, embedding_name: str, file_name: str, file_buffer
) -> Union[int, UploadResponse]:
    total_docs = 0

    with h5py.File(file_buffer, "r") as f:
        ids = f["ids"]
        embs = f["embeddings"]
        upload_batch = []
        for doc_id_str, embedding in zip(ids, embs):
            doc_id = doc_id_str.astype(str)
            fields = {embedding_name: {"values": embedding[:].tolist()}}
            upload_batch.append((datastore_name, doc_id, fields, False))
            # if batch is full, upload and reset
            if len(upload_batch) == settings.VESPA_FEED_BATCH_SIZE:
                vespa_responses = vespa_app.update_batch(upload_batch)
                for i, vespa_response in enumerate(vespa_responses):
                    logger.info(f"Upload of embedding {total_docs}: " + str(vespa_response.json))
                    if vespa_response.status_code != 200:
                        errored_doc_id = upload_batch[i][1]
                        return total_docs, UploadResponse(
                            message=f"Unable to find document with id {errored_doc_id} in datastore.",
                            successful_uploads=total_docs,
                        )
                    total_docs += 1
                upload_batch = []

        # upload remaining
        if len(upload_batch) > 0:
            vespa_responses = vespa_app.update_batch(upload_batch)
            for i, vespa_response in enumerate(vespa_responses):
                logger.info(f"Upload of embedding {total_docs}: " + str(vespa_response.json))
                if vespa_response.status_code != 200:
                    errored_doc_id = upload_batch[i][1]
                    return total_docs, UploadResponse(
                        message=f"Unable to find document with id {errored_doc_id} in datastore.",
                        successful_uploads=total_docs,
                    )
                total_docs += 1

    return total_docs, None


@router.post(
    "/{index_name}/embeddings/upload",
    response_model=UploadResponse,
    status_code=201,
    responses={400: {"model": UploadResponse}},
)
def upload_document_embeddings(
    datastore_name: str,
    index_name: str,
    file: UploadFile = File(...),
    response: Response = None,
):
    embedding_name = Index.get_embedding_field_name(index_name)

    uploaded_docs, upload_response = upload_embeddings_file(datastore_name, embedding_name, file.filename, file.file)
    if upload_response is not None:
        response.status_code = 400
        return upload_response
    else:
        return UploadResponse(
            message=f"Successfully uploaded {uploaded_docs} embeddings.", successful_uploads=uploaded_docs
        )


@router.post(
    "/{index_name}/embeddings",
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
    total_docs = 0  # total uploaded items across all files
    embedding_name = Index.get_embedding_field_name(index_name)

    for url in urlset.urls:
        try:
            r = requests.get(url)
            if r.status_code != 200:
                api_response.status_code = 400
                return UploadResponse(
                    message=f"Failed to retrieve embeddings from {url}.",
                    successful_uploads=total_docs,
                )

            # TODO how to handle files that are too big?
            buffer = BytesIO(r.content)
            uploaded_docs, upload_response = upload_embeddings_file(datastore_name, embedding_name, url, buffer)
            buffer.close()
            if upload_response is not None:
                api_response.status_code = 400
                return upload_response
            total_docs += uploaded_docs
        except requests.exceptions.RequestException:
            api_response.status_code = 400
            return UploadResponse(message=f"Failed to connect to {url}.", successful_uploads=total_docs)

    return UploadResponse(message=f"Successfully uploaded {total_docs} embeddings.", successful_uploads=total_docs)


@router.delete("/{index_name}")
async def delete_index(datastore_name: str = Path(...), index_name: str = Path(...)):
    success = await db.delete_index(datastore_name, index_name)
    # also delete the corresponding query type field if available
    query_embedding_name = Index.get_query_embedding_field_name(index_name)
    query_type_field_name = f"ranking.features.query({query_embedding_name})"
    await db.delete_query_type_field(query_type_field_name)

    if success:
        success &= await package_generator.generate_and_upload(allow_content_removal=True)
        if success:
            return Response(status_code=204)
        else:
            return Response(status_code=500)
    else:
        return Response(status_code=404)


@router.get("/{index_name}/embeddings/{doc_id}", response_model=DocumentEmbedding)
async def get_document_embedding(
    datastore_name: str = Path(...), index_name: str = Path(...), doc_id: str = Path(...)
):
    res = vespa_app.get_data(datastore_name, doc_id)
    doc = res.json
    embedding_name = Index.get_embedding_field_name(index_name)
    # read embedding values from Vespa response
    if res.status_code == 200 and embedding_name in doc["fields"]:
        return DocumentEmbedding.from_vespa(doc, embedding_name)
    return Response(status_code=404)


@router.post("/{index_name}/embeddings/{doc_id}")
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
# @router.post("/{index_name}/indexing")
# async def update_index(
#     datastore_name: str = Path(...), index_name: str = Path(...), reindex: str = Path(...), filtering: list = Body([])
# ):
#     pass
