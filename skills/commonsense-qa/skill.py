import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and a set of answer candidates, predicts the most likely answer."""

    query = request.query
    choices = request.skill_args["choices"]
    prepared_input = [[query, c] for c in choices]

    model_request_kwargs = extract_model_kwargs_from_request(request)

    model_request = {"input": prepared_input, **model_request_kwargs}
    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]
    model_response = square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info(f"Models response:\n{model_response}")

    return QueryOutput.from_sequence_classification(
        questions=query, answers=choices, model_api_output=model_response
    )
