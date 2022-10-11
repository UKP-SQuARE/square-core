import logging
import numpy as np

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import DataAPI, ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()
data_api = DataAPI()


def softmax(x):
    return (np.exp(x)/np.exp(x).sum())


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, performs open-domain, extractive QA. First, background
    knowledge is retrieved using a specified index and retrieval method. Next, the top k
    documents are used for span extraction. Finally, the extracted answers are returned.
    """

    if request.skill_args["feedback_documents"]:
        feedback_docs = request.skill_args["feedback_documents"]
        query = request.query
        data = await data_api(
            datastore_name=request.skill_args["datastore"],
            index_name=request.skill_args.get("index", ""),
            query=query,
            feedback_documents=feedback_docs
        )

        # logger.info(f"Data API output:\n{data}")
        context = [d["document"]["text"] + " Article: https://pubmed.ncbi.nlm.nih.gov/" + d["id"] for d in data]
        context_score = softmax(context_score).round(2).tolist()

        return QueryOutput.from_information_retrieval(
            questions=query,
            context=context,
            context_score=context_score,
        )
    else:
        query = request.query
        data = await data_api(
            datastore_name=request.skill_args["datastore"],
            index_name=request.skill_args.get("index", ""),
            query=query
        )

        # logger.info(f"Data API output:\n{data}")
        context = [d["document"]["text"] + " Article: https://pubmed.ncbi.nlm.nih.gov/" + d["id"] for d in data]
        context_score = softmax(context_score).round(2).tolist()

        return QueryOutput.from_information_retrieval(
            questions=query,
            context=context,
            context_score=context_score,
        )
