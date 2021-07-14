from fastapi import APIRouter, File, UploadFile
from fastapi.param_functions import Path, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..core.vespa_app import vespa_app


router = APIRouter(tags=["Documents"])


class Document(BaseModel):
    title: str
    text: str


@router.post(
    "/datastore/{datastore_name}/documents/{doc_id}"
)
def insert_document(datastore_name: str, doc_id: int, document: Document):
    response = vespa_app.feed_data_point(
        schema=datastore_name,
        data_id=doc_id,
        fields={
            "title": document.title,
            "text": document.text,
        },
    )
    return response


@router.get(
    "/datastore/{datastore_name}/documents/{doc_id}"
)
def get_document(datastore_name: str, doc_id: int):
    response = vespa_app.get_data(datastore_name, doc_id)
    return response


@router.put(
    "/datastore/{datastore_name}/documents/{doc_id}"
)
def update_document(datastore_name: str, doc_id: int, document: Document):
    response = vespa_app.update_data(
        datastore_name,
        doc_id,
        {"title": document.title, "text": document.text},
        create=True
    )
    return response


@router.delete(
    "/datastore/{datastore_name}/documents/{doc_id}"
)
def delete_document(datastore_name: str, doc_id: int):
    response = vespa_app.delete_data(
        schema="wiki", 
        data_id=doc_id,
    )
    return response


@router.post(
    "/datastore/{datastore_name}/documents"
)
async def insert_batch_documents(datastore_name: str, documents: UploadFile = File(...)):
    content = await documents.read()
    num_inserted = 0
    for document in content.decode("utf-8").split("\n"):
        splitted = document.split("\t")
        if len(splitted) < 3:
            continue
        response = vespa_app.feed_data_point(
            schema=datastore_name,
            data_id=splitted[0],
            fields={
                "title": splitted[1],
                "text": splitted[2],
            },
        )
        if response.status_code == 200:
            num_inserted += 1

    return {"#successfully inserted": num_inserted}


@router.get(
    "/datastore/{datastore_name}/documents"
)
async def get_batch_documents(datastore_name: str):
    endpoint = "{}/document/v1/{}/{}/docid".format(vespa_app.end_point, datastore_name, datastore_name)
    response = vespa_app.http_session.get(endpoint, cert=vespa_app.cert)
    documents = [{"id": doc["id"], "title": doc["fields"]["title"], "text": doc["fields"]["text"]} for doc in response.json()["documents"]]
    continuation = response.json()["continuation"]
    while continuation is not None:
        vespa_format = {
            "continuation": continuation,
        }
        response = vespa_app.http_session.get(endpoint, params=vespa_format, cert=vespa_app.cert)
        documents += [{"id": doc["id"], "title": doc["fields"]["title"], "text": doc["fields"]["text"]} for doc in response.json()["documents"]]
        if "continuation" in response.json():
            continuation = response.json()["continuation"]
        else:
            break
    # with open("test.tsv", "w+", encoding="utf-8") as output_file:
    #     for doc in documents:
    #         output_file.write("{}\t{}\t{}\n".format(doc["id"], doc["title"], doc["text"]))
    return {"documents": documents} # FileResponse("test.tsv")
