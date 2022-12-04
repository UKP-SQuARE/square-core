import logging

import numpy as np
from square_datastore_client import SQuAREDatastoreClient
from square_skill_api.models import QueryOutput, QueryRequest

logger = logging.getLogger(__name__)

square_datastore_client = SQuAREDatastoreClient()


def softmax(x):
    return np.exp(x) / np.exp(x).sum()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, performs open-domain, extractive QA. First, background
    knowledge is retrieved using a specified index and retrieval method. Next, the top k
    documents are used for span extraction. Finally, the extracted answers are returned.
    """

    if "feedback_documents" in request.skill_args:
        feedback_docs = request.skill_args["feedback_documents"]
        query = request.query
        data_response = await square_datastore_client(
            datastore_name=request.skill_args["datastore"],
            index_name=request.skill_args.get("index", ""),
            query=query,
            feedback_documents=feedback_docs,
        )
    else:
        query = request.query
        data_response = await square_datastore_client(
            datastore_name=request.skill_args["datastore"],
            index_name=request.skill_args.get("index", ""),
            query=query,
        )

    context = []
    if request.skill_args["datastore"] == "bioasq":
        for d in data_response:
            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{d['id']}"
            d["document"][
                "text"
            ] = f"""{d["document"]["text"]} <p><a href="{pubmed_url}" target="_blank">{pubmed_url}</a></p>"""
            context.append(d["document"]["text"])
    else:
        context = [d["document"]["text"] for d in data_response]

    context_score = [d["score"] for d in data_response]
    context_score = softmax(context_score).round(2).tolist()

    return QueryOutput.from_information_retrieval(
        questions=query,
        context=context,
        context_score=context_score,
    )
