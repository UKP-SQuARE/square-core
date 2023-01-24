import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Predicts yes/no for a boolean question with context"""
    query = request.query
    context = request.skill_args["context"]

    model_request_kwargs = extract_model_kwargs_from_request(request)

    prepared_input = [[context, query]]

    model_request = {
        "input": prepared_input,
        "adapter_name": request.skill_args["adapter"],
        **model_request_kwargs,
    }
    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info(f"Models response:\n{model_response}")

    return QueryOutput.from_sequence_classification(
        questions=query,
        answers=["No", "Yes"],
        model_api_output=model_response,
        context=context,
    )
