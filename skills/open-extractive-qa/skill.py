import logging
from typing import Iterable

from square_skill_api.models import QueryOutput, QueryRequest

from square_model_client import SQuAREModelClient
from square_datastore_client import SQuAREDatastoreClient

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
square_datastore_client = SQuAREDatastoreClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, performs open-domain, extractive QA. First, background
    knowledge is retrieved using a specified index and retrieval method. Next, the top k
    documents are used for span extraction. Finally, the extracted answers are returned.
    """

    query = request.query
    explain_kwargs = request.explain_kwargs or {}
    attack_kwargs = request.attack_kwargs or {}

    context = request.skill_args.get("context")
    if not context:
        data_response = await square_datastore_client(
            datastore_name=request.skill_args["datastore"],
            index_name=request.skill_args.get("index", ""),
            query=query,
        )
        logger.info(f"Data response:\n{data_response}")
        context = [d["document"]["text"] for d in data_response]
        context_score = [d["score"] for d in data_response]

        prepared_input = [[query, c] for c in context]
    else:
        # skip backgrond knowledge retrieval and use context provided
        prepared_input = [[query, context]]
        context_score = 1

    model_request = {
        "input": prepared_input,
        "task_kwargs": {"topk": request.skill_args.get("topk", 5)},
        "explain_kwargs": explain_kwargs,
        "attack_kwargs": attack_kwargs,
    }
    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]
    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return QueryOutput.from_question_answering(
        questions=query,
        model_api_output=model_response,
        context=context,
        context_score=context_score,
    )
