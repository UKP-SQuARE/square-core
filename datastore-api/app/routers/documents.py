import json
from typing import Dict

import requests
from fastapi import APIRouter, Response
from fastapi.param_functions import Path, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from ..core.config import settings
from ..core.utils import get_fields
from ..core.vespa_app import vespa_app
from ..models.upload import UploadResponse, UploadUrlSet


router = APIRouter(tags=["Documents"])


class Document(BaseModel):
    data: Dict[str, str]


@router.post("/datastore/{datastore_name}/documents/{doc_id}")
async def insert_document(datastore_name: str, doc_id: int, document: Document):
    fields = await get_fields(datastore_name)
    if not all([field in fields for field in document.data]):
        return PlainTextResponse(status_code=404, content="The datastore does not contain at least one of the fields {}".format(" ".join(document.data.keys())))

    response = vespa_app.feed_data_point(
        schema=datastore_name,
        data_id=doc_id,
        fields={
            field: document.data[field]
            for field in fields
        },
    )
    return response


@router.get("/datastore/{datastore_name}/documents/{doc_id}")
def get_document(datastore_name: str, doc_id: int):
    response = vespa_app.get_data(datastore_name, doc_id)
    return response


@router.put("/datastore/{datastore_name}/documents/{doc_id}")
async def update_document(datastore_name: str, doc_id: int, document: Document):
    fields = await get_fields(datastore_name)
    if not all([field in fields for field in document.data]):
        return PlainTextResponse(status_code=404, content="The datastore does not contain at least one of the fields {}".format(" ".join(document.data.keys())))
    response = vespa_app.update_data(
        datastore_name, doc_id, document.data, create=True
    )
    return response


@router.delete("/datastore/{datastore_name}/documents/{doc_id}")
def delete_document(datastore_name: str, doc_id: int):
    response = vespa_app.delete_data(
        schema="wiki",
        data_id=doc_id,
    )
    return response


@router.post(
    "/datastore/{datastore_name}/documents",
    response_model=UploadResponse,
    status_code=201,
    responses={400: {"model": UploadResponse}},
)
def upload_documents_from_urls(datastore_name: str, urlset: UploadUrlSet, api_response: Response):
    doc_count = 0

    for url in urlset.urls:
        with requests.get(url, stream=True) as r:
            if r.status_code != 200:
                api_response.status_code = 400
                return UploadResponse(
                    message=f"Failed to retrieve documents from {url}.",
                    successful_uploads=doc_count,
                )

            upload_batch = []
            for i, line in enumerate(r.iter_lines()):
                try:
                    doc_data = json.loads(line)
                    doc_id = doc_data.pop("id")
                    upload_batch.append({"id": doc_id, "fields": doc_data})
                    doc_count += 1
                except Exception:
                    api_response.status_code = 400
                    return UploadResponse(
                        message=f"Unable to correctly decode document {i} in {url}.",
                        successful_uploads=doc_count,
                    )
                if doc_count % settings.VESPA_FEED_BATCH_SIZE == 0:
                    vespa_responses = vespa_app.feed_batch(datastore_name, upload_batch)
                    for i, vespa_response in enumerate(vespa_responses):
                        print(vespa_response.json)
                        if vespa_response.status_code != 200:
                            api_response.status_code = 400
                            errored_doc_id = upload_batch[i][1]
                            return UploadResponse(
                                message=f"Unable to upload document with id {errored_doc_id} to datastore.",
                                successful_uploads=doc_count,
                            )
                    upload_batch = []

    return UploadResponse(message=f"Successfully uploaded {doc_count} documents.", successful_uploads=doc_count)


@router.get("/datastore/{datastore_name}/documents")
async def get_all_documents(datastore_name: str):
    endpoint = "{}/document/v1/{}/{}/docid".format(vespa_app.end_point, datastore_name, datastore_name)
    response = vespa_app.http_session.get(endpoint, cert=vespa_app.cert)
    fields = await get_fields(datastore_name)
    documents = []
    for doc in response.json()["documents"]:
        tmp = {field: doc["fields"][field] for field in doc["fields"] if field in fields}
        tmp["id"] = doc["id"]
        documents.append(tmp)
    continuation = None
    if "continuation" in response.json():
        continuation = response.json()["continuation"]
    while continuation is not None:
        vespa_format = {
            "continuation": continuation,
        }
        response = vespa_app.http_session.get(endpoint, params=vespa_format, cert=vespa_app.cert)
        for doc in response.json()["documents"]:
            tmp = {field: doc["fields"][field] for field in doc["fields"] if field in fields}
            tmp["id"] = doc["id"]
            documents.append(tmp)
        if "continuation" in response.json():
            continuation = response.json()["continuation"]
        else:
            break
    # with open("test.tsv", "w+", encoding="utf-8") as output_file:
    #     for doc in documents:
    #         output_file.write("{}\t{}\t{}\n".format(doc["id"], doc["title"], doc["text"]))
    return {"documents": documents}  # FileResponse("test.tsv")
