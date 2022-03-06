import json
import logging
from typing import Iterable, List, Union

import requests
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from fastapi.param_functions import Body, Path
from fastapi.responses import StreamingResponse

from ..core.config import settings
from ..models.document import Document
from ..models.httperror import HTTPError
from ..models.upload import UploadResponse, UploadUrlSet
from .dependencies import get_storage_connector


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])


async def upload_document_file(
    conn, datastore_name: str, file_name: str, file_iterator: Iterable
) -> Union[int, UploadResponse]:
    total_docs = 0
    upload_batch = []
    for i, line in enumerate(file_iterator):
        try:
            doc_data = json.loads(line)
            upload_batch.append(Document(__root__=doc_data))
        except Exception:
            return total_docs, UploadResponse(
                message=f"Unable to correctly decode document {i} in {file_name}.",
                successful_uploads=total_docs,
            )
        # if batch is full, upload and reset
        if len(upload_batch) == settings.UPLOAD_BATCH_SIZE:
            successes, errors = await conn.add_document_batch(datastore_name, upload_batch)
            if errors > 0:
                return total_docs, UploadResponse(
                    message=f"Unable to upload {errors} documents from {file_name}.",
                    successful_uploads=total_docs,
                )
            total_docs += successes
            upload_batch = []

    # upload remaining
    if len(upload_batch) > 0:
        successes, errors = await conn.add_document_batch(datastore_name, upload_batch)
        if errors > 0:
            return total_docs, UploadResponse(
                message=f"Unable to upload {errors} documents from {file_name}.",
                successful_uploads=total_docs,
                errors=errors,
            )
        total_docs += successes

    return total_docs, None


@router.post(
    "/upload",
    summary="Upload documents from a file to the datastore",
    description="Upload all documents from a  jsonl file to the datastore",
    response_model=UploadResponse,
    status_code=201,
    responses={
        200: {"description": "Number of successfully uploaded documents to the datastore."},
        400: {"model": UploadResponse, "description": "Error during Upload"},
        404: {"model": HTTPError, "description": "The datastore does not exist."},
    },
)
async def upload_documents(
    datastore_name: str = Path(..., description="The name of the datastore"),
    file: UploadFile = File(..., description="The filecontaining the documents to upload"),
    conn=Depends(get_storage_connector),
    response: Response = None,
):
    datastore = await conn.get_datastore(datastore_name)
    if datastore is None:
        raise HTTPException(status_code=404, detail="Datastore not found.")

    uploaded_docs, upload_response = await upload_document_file(conn, datastore_name, file.filename, file.file)
    if upload_response is not None:
        response.status_code = 400
        return upload_response
    else:
        return UploadResponse(
            message=f"Successfully uploaded {uploaded_docs} documents.", successful_uploads=uploaded_docs
        )


@router.post(
    "/from_urls",
    summary="Upload documents from a file at the given url to the datastore",
    response_model=UploadResponse,
    status_code=201,
    responses={
        201: {"description": "Number of successfully uploaded documents to the datastore."},
        400: {"model": UploadResponse, "description": "Error during Upload"},
        404: {"model": HTTPError, "description": "The datastore does not exist."},
    },
)
async def upload_documents_from_urls(
    datastore_name: str = Path(..., description="The name of the datastore"),
    urlset: UploadUrlSet = Body(..., description="The url containing the documents to upload"),
    conn=Depends(get_storage_connector),
    api_response: Response = None,
):
    datastore = await conn.get_datastore(datastore_name)
    if datastore is None:
        raise HTTPException(status_code=404, detail="Datastore not found.")

    total_docs = 0  # total uploaded items across all files

    for url in urlset.urls:
        try:
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                api_response.status_code = 400
                return UploadResponse(
                    message=f"Failed to retrieve documents from {url}.",
                    successful_uploads=total_docs,
                )

            uploaded_docs, upload_response = await upload_document_file(conn, datastore_name, url, r.iter_lines())
            if upload_response is not None:
                api_response.status_code = 400
                return upload_response
            total_docs += uploaded_docs
            r.close()
        except requests.exceptions.RequestException:
            api_response.status_code = 400
            return UploadResponse(message=f"Failed to connect to {url}.", successful_uploads=total_docs)

    return UploadResponse(message=f"Successfully uploaded {total_docs} documents.", successful_uploads=total_docs)


@router.post(
    "",
    summary="Upload a batch of documents",
    response_model=UploadResponse,
    status_code=201,
    responses={
        200: {"description": "Number of successfully uploaded documents to the datastore."},
        400: {"model": UploadResponse, "description": "Error during Upload"},
        404: {"model": HTTPError, "description": "The datastore does not exist."},
        422: {"description": "Cannot instantiate a Document object"}
    },
)
async def post_documents(
    datastore_name: str = Path(..., description="The name of the datastore"),
    documents: List[Document] = Body(..., description="Batch of documents to be uploaded."),
    conn=Depends(get_storage_connector),
    response: Response = None,
):
    datastore = await conn.get_datastore(datastore_name)
    if datastore is None:
        raise HTTPException(status_code=404, detail="Datastore not found.")

    successes, errors = await conn.add_document_batch(datastore_name, documents)
    if errors > 0:
        response.status_code = 400
        return UploadResponse(
            message=f"Unable to upload {errors} documents.", successful_uploads=successes, errors=errors
        )
    else:
        return UploadResponse(message=f"Successfully uploaded {successes} documents.", successful_uploads=successes)


#TODO: Remove this and use the collection_url from the index meta data instead
@router.get(
    "",
    summary="Get all documents from the datastore",
    description="Lists all documents from the datastore",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "List of all documents in the datastore",
        },
        400: {"model": HTTPError, "description": "Exception during retrieval"},
    },
)
async def get_all_documents(
    datastore_name: str = Path(..., description="The name of the datastore"),
    conn=Depends(get_storage_connector),
):
    async def yield_documents():
        async for doc in conn.get_documents(datastore_name):
            yield doc.json() + "\n"

    return StreamingResponse(yield_documents(), media_type="application/octet-stream")


@router.get(
    "/{doc_id}",
    summary="Get a document from the datastore",
    description="Get a document from the datastore by id",
    responses={
        200: {
            "description": "The document",
            "model": Document,
        },
        400: {"model": HTTPError, "description": "Failed to retrieve document"},
    },
)
async def get_document(
    datastore_name: str = Path(..., description="The name of the datastore"),
    doc_id: str = Path(..., description="The id of the document to retrieve"),
    conn=Depends(get_storage_connector),
):
    result = await conn.get_document(datastore_name, doc_id)
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find document.")


@router.put(
    "/{doc_id}",
    summary="Update a document in the datastore",
    description="Update a document in the datastore by id",
    responses={
        200: {"description": "The document has been created successfully."},
        201: {"description": "The document has been created successfully."},
        400: {"model": HTTPError, "description": "Failed to update document"},
        422: {"description": "Cannot instantiate a Document object"}
    },
)
async def update_document(
    request: Request,
    datastore_name: str = Path(..., description="The name of the datastore"),
    doc_id: str = Path(..., description="The id of the document to update"),
    document: Document = Body(..., description="The document to update"),
    conn=Depends(get_storage_connector),
):
    datastore = await conn.get_datastore(datastore_name)
    if datastore is None:
        raise HTTPException(status_code=404, detail="Datastore not found.")

    # First, check if all fields in the uploaded document are valid.
    if not datastore.is_valid_document(document):
        raise HTTPException(
            status_code=400,
            detail="The given document does not have the correct format.",
        )
    # also check if the doc id in the body matches the path
    if doc_id != document.id:
        raise HTTPException(
            status_code=400,
            detail="The document ID specified in the path and in the request body must match.",
        )

    success, created = await conn.add_document(datastore_name, doc_id, document)
    if success:
        if not created:
            status_code = 200
        else:
            status_code = 201
        return Response(
            status_code=status_code,
            headers={"Location": request.url_for("get_document", datastore_name=datastore_name, doc_id=doc_id)},
        )
    else:
        raise HTTPException(status_code=500)


@router.delete(
    "/{doc_id}",
    summary="Delete a document from the datastore",
    description="Delete a document from the datastore by id",
    responses={204: {"description": "The document was deleted"}},
)
async def delete_document(
    datastore_name: str = Path(..., description="The name of the datastore"),
    doc_id: str = Path(..., description="The id of the document to delete"),
    conn=Depends(get_storage_connector),
):
    success = await conn.delete_document(datastore_name, doc_id)
    if success:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find document to delete.")
