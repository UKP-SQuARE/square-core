import logging
from io import BytesIO
from typing import List, Union

import h5py
import numpy as np
import requests
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.param_functions import Body, Path, Query
from fastapi.responses import JSONResponse, StreamingResponse

from ..core.config import settings
from ..core.utils import create_index_object
from ..models.embedding import DocumentEmbedding
from ..models.httperror import HTTPError
from ..models.index import Index, IndexRequest, IndexResponse
from ..models.upload import UploadResponse, UploadUrlSet
from .dependencies import get_storage_connector


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Indices"])


@router.get(
    "",
    summary="Lists all indices of a datastore",
    description="Returns a list of all indices in a datastore.",
    responses={
        200: {
            "description": "List of all indices found",
            "model": List[IndexResponse],
        }
    },
)
async def get_all_indices(
    datastore_name: str = Path(..., description="Datastore name"),
    conn=Depends(get_storage_connector),
):
    indices = await conn.get_indices(datastore_name)
    return [IndexResponse.from_index(index) for index in indices]


@router.get(
    "/{index_name}",
    summary="Get an index by its name",
    description="Returns an index for a datastore given its name.",
    responses={
        200: {"model": IndexResponse, "description": "The requested index"},
        404: {
            "description": "The requested index does not exist",
            "model": HTTPError,
        },
    },
)
async def get_index(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    conn=Depends(get_storage_connector),
):
    index = await conn.get_index(datastore_name, index_name)
    if index is None:
        raise HTTPException(status_code=404, detail="Index not found.")
    else:
        return IndexResponse.from_index(index)


@router.put(
    "/{index_name}",
    summary="Creates a new index or updates it if it exists",
    description="Creates a new index in  the specified datastore of a index with that name allready exists it is updated to the given configuration",
    responses={
        200: {"model": IndexResponse, "description": "The configuration of the updated index"},
        201: {"model": IndexResponse, "description": "The configuration of the created index"},
        400: {"model": HTTPError, "description": "The creation of the index failed in the API database"},
        500: {"model": HTTPError, "description": "The update of the index failed in VESPA"},
    },
)
async def put_index(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    index_request: IndexRequest = Body(..., description="The index configuration as IndexRequest"),
    conn=Depends(get_storage_connector),
    response: Response = None,
):
    index = await conn.get_index(datastore_name, index_name)
    if index is None:
        new_index = await create_index_object(datastore_name, index_name, index_request)
        success = await conn.add_index(new_index) is not None
        response.status_code = status.HTTP_201_CREATED
    else:
        new_index = await create_index_object(datastore_name, index_name, index_request)
        success = await conn.update_index(new_index)
        response.status_code = status.HTTP_200_OK

    if success:
        await conn.commit_changes()
        return IndexResponse.from_index(new_index)
    else:
        raise HTTPException(status_code=400)


@router.get("/{index_name}/status")
async def get_index_status(
    datastore_name: str = Path(...),
    index_name: str = Path(...),
    conn=Depends(get_storage_connector),
):
    index = await conn.get_index(datastore_name, index_name)
    status = {"bm25": index.bm25}
    yql = "select * from sources {} where  id > 0;".format(datastore_name)
    request = requests.get(settings.VESPA_APP_URL + "/search/", params={"yql": yql})
    if requests.status_codes == 404:
        raise HTTPException(status_code=404, detail="Could not get index status")
    status["total"] = request.json()["root"]["fields"]["totalCount"]

    if not status["bm25"]:
        pass
        # TODO Get number of documents with embedding
    return status


@router.get(
    "/{index_name}/embeddings",
    summary="Get embeddings for all documents in index",
    description="Returns the embeddings for all documents in a given index",
    responses={
        200: {"description": "The embeddings for the documents as a file"},
        400: {"model": HTTPError, "description": "An error occurred while retrieveing the embeddings"},
    },
)
async def get_document_embeddings(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    offset: int = Query(0, description="Offset of the document embedings to retrieve"),
    size: int = Query(1000, description="Size of retrieved batches"),
):
    if size > settings.MAX_RETURN_ITEMS:
        return HTTPException(
            status_code=400, detail="Size cannot be greater than {}".format(settings.MAX_RETURN_ITEMS)
        )

    # TODO implement GET all embeddings
    raise NotImplementedError()
    # embedding_name = Index.get_embedding_field_name(index_name)
    # # TODO This assumes id is always numeric
    # batch = [(datastore_name, i) for i in range(offset, offset + size)]
    # vespa_responses = vespa_app.get_batch(batch)
    # ids, embs = [], []
    # for response in vespa_responses:
    #     if response.status_code == 200 and embedding_name in response.json["fields"]:
    #         doc_embedding = DocumentEmbedding.from_vespa(response.json, embedding_name)
    #         ids.append(doc_embedding.id)
    #         embs.append(doc_embedding.embedding)

    # buffer = BytesIO()
    # with h5py.File(buffer, "w") as f:
    #     f.create_dataset("ids", data=np.array(ids, dtype="S"), compression="gzip")
    #     f.create_dataset("embeddings", data=np.array(embs), compression="gzip")
    # buffer.seek(0)
    # return StreamingResponse(buffer, media_type="application/octet-stream")


def upload_embeddings_file(
    datastore_name: str = Path(..., description="Name of the datastore"),
    embedding_name: str = Path(..., description="Name of the embedding field"),
    file_name: str = Query(..., description="Name of the file containing embeddings to upload"),
    file_buffer=Body(...),
) -> Union[int, UploadResponse]:
    # TODO: implement embedding upload
    raise NotImplementedError()
    # total_docs = 0

    # with h5py.File(file_buffer, "r") as f:
    #     ids = f["ids"]
    #     embs = f["embeddings"]
    #     upload_batch = []
    #     for doc_id_str, embedding in zip(ids, embs):
    #         doc_id = doc_id_str.astype(str)
    #         fields = {embedding_name: {"values": embedding[:].tolist()}}
    #         upload_batch.append((datastore_name, doc_id, fields, False))
    #         # if batch is full, upload and reset
    #         if len(upload_batch) == settings.VESPA_FEED_BATCH_SIZE:
    #             vespa_responses = vespa_app.update_batch(upload_batch)
    #             for i, vespa_response in enumerate(vespa_responses):
    #                 logger.info(f"Upload of embedding {total_docs}: " + str(vespa_response.json))
    #                 if vespa_response.status_code != 200:
    #                     errored_doc_id = upload_batch[i][1]
    #                     return total_docs, UploadResponse(
    #                         message=f"Unable to find document with id {errored_doc_id} in datastore.",
    #                         successful_uploads=total_docs,
    #                     )
    #                 total_docs += 1
    #             upload_batch = []

    #     # upload remaining
    #     if len(upload_batch) > 0:
    #         vespa_responses = vespa_app.update_batch(upload_batch)
    #         for i, vespa_response in enumerate(vespa_responses):
    #             logger.info(f"Upload of embedding {total_docs}: " + str(vespa_response.json))
    #             if vespa_response.status_code != 200:
    #                 errored_doc_id = upload_batch[i][1]
    #                 return total_docs, UploadResponse(
    #                     message=f"Unable to find document with id {errored_doc_id} in datastore.",
    #                     successful_uploads=total_docs,
    #                 )
    #             total_docs += 1

    # return total_docs, None


@router.post(
    "/{index_name}/embeddings/upload",
    response_model=UploadResponse,
    status_code=201,
    summary="Upload embeddings for documents in an index",
    description="Uploads a file containing embeddings for documents in the index",
    responses={
        400: {"model": UploadResponse, "description": "An error occurred while uploading the embeddings"},
        201: {"model": UploadResponse, "description": "The number of embeddings uploaded successfully"},
    },
)
def upload_document_embeddings(
    datastore_name: str = Path(..., description="Name of the datastore"),
    index_name: str = Path(..., description="Name of the index"),
    file: UploadFile = File(..., description="File containing the embeddings"),
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
    responses={
        200: {"model": UploadResponse, "description": "The number of embeddings uploaded successfully"},
        400: {"model": UploadResponse, "description": "An error occurred while uploading the embeddings"},
    },
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


@router.delete(
    "/{index_name}",
    summary="Delete an index",
    description="Deletes the index with the corresponding name and all embeddings contained in the index",
    responses={
        204: {"description": "Successfully deleted index"},
        404: {"model": HTTPError, "description": "Failed to delete index in API database"},
        500: {"model": HTTPError, "description": "Failed to delete index in vespa"},
    },
)
async def delete_index(
    datastore_name: str = Path(..., description="The name of the datastore"),
    index_name: str = Path(..., description="The name of the index"),
    conn=Depends(get_storage_connector),
):
    success = await conn.delete_index(datastore_name, index_name)

    if success:
        await conn.commit_changes()
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)


@router.get(
    "/{index_name}/embeddings/{doc_id}",
    summary="Get embedding for a document",
    description="Returns the embedding for a document in the indexwith the given id",
    responses={
        200: {"model": DocumentEmbedding, "description": "The embedding for the document with the given id"},
        404: {"model": HTTPError, "description": "Failed to find embedding for document with given id"},
    },
    response_model=DocumentEmbedding,
)
async def get_document_embedding(
    datastore_name: str = Path(..., description="The name of the datastore"),
    index_name: str = Path(..., description="The name of the index"),
    doc_id: str = Path(..., description="The id of the document"),
):
    # TODO implement GET embedding
    raise NotImplementedError()
    # res = vespa_app.get_data(datastore_name, doc_id)
    # doc = res.json
    # embedding_name = Index.get_embedding_field_name(index_name)
    # # read embedding values from Vespa response
    # if res.status_code == 200 and embedding_name in doc["fields"]:
    #     return DocumentEmbedding.from_vespa(doc, embedding_name)
    # raise HTTPException(status_code=404)


@router.post(
    "/{index_name}/embeddings/{doc_id}",
    summary="Set embedding for a document",
    description="Set the embedding for a document in the index with the given id",
    responses={
        200: {"description": "Successfully set embedding for document with given id"},
    },
)
async def set_document_embedding(
    datastore_name: str = Path(..., description="The name of the datastore"),
    index_name: str = Path(..., description="The name of the index"),
    doc_id: str = Path(..., description="The id of the document"),
    embedding: List[float] = Body(..., description="The embedding for the document"),
):
    # TODO implement POST embedding
    raise NotImplementedError()
    # # check whether document exists, vespa is not returning that information
    # if vespa_app.get_data(datastore_name, doc_id).status_code != 200:
    #     raise HTTPException(status_code=404, detail="Document does not exist")
    # embedding_name = Index.get_embedding_field_name(index_name)
    # fields = {embedding_name: {"values": embedding}}
    # response = vespa_app.update_data(datastore_name, doc_id, fields)
    # return JSONResponse(status_code=response.status_code, content=response.json)


# TODO
# @router.post("/{index_name}/indexing")
# async def update_index(
#     datastore_name: str = Path(...), index_name: str = Path(...), reindex: str = Path(...), filtering: list = Body([])
# ):
#     pass
