import json
import logging
from typing import Iterable, Union

import requests
from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile
from fastapi.param_functions import Body, Path, Query
from fastapi.responses import JSONResponse, StreamingResponse

from ..core.config import settings
from ..core.utils import get_fields
from ..core.vespa_app import vespa_app
from ..models.document import Document
from ..models.httperror import HTTPError
from ..models.upload import UploadResponse, UploadUrlSet


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])


def upload_document_file(datastore_name: str, file_name: str, file_iterator: Iterable) -> Union[int, UploadResponse]:
    total_docs = 0
    upload_batch = []
    for i, line in enumerate(file_iterator):
        try:
            doc_data = json.loads(line)
            # get doc id
            doc_id = doc_data.get("id")
            upload_batch.append({"id": doc_id, "fields": doc_data})
        except Exception:
            return total_docs, UploadResponse(
                message=f"Unable to correctly decode document {i} in {file_name}.",
                successful_uploads=total_docs,
            )
        # if batch is full, upload and reset
        if len(upload_batch) == settings.VESPA_FEED_BATCH_SIZE:
            vespa_responses = vespa_app.feed_batch(datastore_name, upload_batch)
            for i, vespa_response in enumerate(vespa_responses):
                logger.info(f"Upload of document {total_docs}: " + str(vespa_response.json))
                if vespa_response.status_code != 200:
                    errored_doc_id = upload_batch[i][1]
                    return total_docs, UploadResponse(
                        message=f"Unable to upload document with id {errored_doc_id} to datastore.",
                        successful_uploads=total_docs,
                    )
                total_docs += 1
            upload_batch = []

    # upload remaining
    if len(upload_batch) > 0:
        vespa_responses = vespa_app.feed_batch(datastore_name, upload_batch)
        for i, vespa_response in enumerate(vespa_responses):
            logger.info(f"Upload of document {total_docs}: " + str(vespa_response.json))
            if vespa_response.status_code != 200:
                errored_doc_id = upload_batch[i][1]
                return total_docs, UploadResponse(
                    message=f"Unable to upload document with id {errored_doc_id} to datastore.",
                    successful_uploads=total_docs,
                )
            total_docs += 1

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
    },
)
def upload_documents(
    datastore_name: str = Path(..., description="The name of the datastore"),
    file: UploadFile = File(..., description="The filecontaining the documents to upload"),
    response: Response = None,
):
    uploaded_docs, upload_response = upload_document_file(datastore_name, file.filename, file.file)
    if upload_response is not None:
        response.status_code = 400
        return upload_response
    else:
        return UploadResponse(
            message=f"Successfully uploaded {uploaded_docs} documents.", successful_uploads=uploaded_docs
        )


@router.post(
    "",
    summary="Upload documents from a file at the given url to the datastore",
    response_model=UploadResponse,
    responses={
        201: {"description": "Number of successfully uploaded documents to the datastore."},
        400: {"model": UploadResponse, "description": "Error during Upload"},
    },
)
def upload_documents_from_urls(
    datastore_name: str = Path(..., description="The name of the datastore"),
    urlset: UploadUrlSet = Body(..., description="The url containing the documents to upload"),
    api_response: Response = None,
):
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

            uploaded_docs, upload_response = upload_document_file(datastore_name, url, r.iter_lines())
            if upload_response is not None:
                api_response.status_code = 400
                return upload_response
            total_docs += uploaded_docs
            r.close()
        except requests.exceptions.RequestException:
            api_response.status_code = 400
            return UploadResponse(message=f"Failed to connect to {url}.", successful_uploads=total_docs)

    return UploadResponse(message=f"Successfully uploaded {total_docs} documents.", successful_uploads=total_docs)


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
    offset: int = Query(0, description="The offset to start the list"),
    size: int = Query(1000, description="The number of documents in one batch retrieved from vespa"),
):
    if size > settings.MAX_RETURN_ITEMS:
        return HTTPException(
            status_code=400, detail="Size cannot be greater than {}".format(settings.MAX_RETURN_ITEMS)
        )

    fields = await get_fields(datastore_name)
    # TODO This assumes id is always numeric
    batch = [(datastore_name, i) for i in range(offset, offset + size)]
    vespa_responses = vespa_app.get_batch(batch)

    def yield_documents():
        for response in vespa_responses:
            if response.status_code == 200:
                yield Document.from_vespa(response.json, fields).json() + "\n"

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
    doc_id: int = Path(..., description="The id of the document to retrieve"),
):
    response = vespa_app.get_data(datastore_name, doc_id)
    if response.status_code == 200:
        fields = await get_fields(datastore_name)
        return Document.from_vespa(response.json, fields)
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json)


@router.post(
    "/{doc_id}",
    summary="Upload a document in the datastore",
    description="Upload a document in the datastore by id",
    responses={
        200: {"class": Response, "description": "The location of the uploaded document"},
        400: {"model": HTTPError, "description": "Failed to upload document"},
    },
)
async def post_document(
    request: Request,
    datastore_name: str = Path(..., description="The name of the datastore"),
    doc_id: int = Path(..., description="The id of the document to upload"),
    document: Document = Body(..., description="The document to upload"),
):
    fields = await get_fields(datastore_name)
    if not all([field in fields for field in document]):
        raise HTTPException(
            status_code=404,
            detail="The datastore does not contain at least one of the fields {}".format(" ".join(document.keys())),
        )

    vespa_response = vespa_app.feed_data_point(
        schema=datastore_name,
        data_id=doc_id,
        fields={**document, "id": doc_id},
    )
    if vespa_response.status_code == 200:
        return Response(
            status_code=201,
            headers={"Location": request.url_for("get_document", datastore_name=datastore_name, doc_id=doc_id)},
        )
    else:
        raise HTTPException(status_code=vespa_response.status_code, detail=vespa_response.json)


@router.put(
    "/{doc_id}",
    summary="Update a document in the datastore",
    description="Update a document in the datastore by id",
    responses={
        200: {"class": Response, "description": "The location of the updated document"},
        400: {"model": HTTPError, "description": "Failed to update document"},
    },
)
async def update_document(
    request: Request,
    datastore_name: str = Path(..., description="The name of the datastore"),
    doc_id: int = Path(..., description="The id of the document to update"),
    document: Document = Body(..., description="The document to update"),
):
    fields = await get_fields(datastore_name)
    if not all([field in fields for field in document]):
        return HTTPException(
            status_code=404,
            detail="The datastore does not contain at least one of the fields {}".format(" ".join(document.keys())),
        )

    doc_fields = {**document, "id": doc_id}
    vespa_response = vespa_app.update_data(datastore_name, doc_id, doc_fields, create=True)
    if vespa_response.status_code == 200:  # TODO Vespa doesn't distinguish between 200 and 201
        return Response(
            status_code=200,
            headers={"Location": request.url_for("get_document", datastore_name=datastore_name, doc_id=doc_id)},
        )
    else:
        raise HTTPException(status_code=vespa_response.status_code, detail=vespa_response.json)


@router.delete(
    "/{doc_id}",
    summary="Delete a document from the datastore",
    description="Delete a document from the datastore by id",
    responses={204: {"description": "The document was deleted"}},
)
def delete_document(
    datastore_name: str = Path(..., description="The name of the datastore"),
    doc_id: int = Path(..., description="The id of the document to delete"),
):
    response = vespa_app.delete_data(
        schema="wiki",
        data_id=doc_id,
    )
    if response.status_code == 200:  # TODO Vespa isn't returning any useful status codes on delete
        return Response(status_code=204)
    else:
        return JSONResponse(status_code=response.status_code, content=response.json)
