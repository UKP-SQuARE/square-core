import logging

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and context, performs extractive QA. This skill is a general
    skill, it can be used with any adapter for extractive question answering. The
    adapter to use can be specified in the `skill_args` or via the `default_skill_args`
    in the skill-manager.
    """

    query = request.query
    context = request.skill_args["context"]
    prepared_input = [[query, context]]

    model_request_kwargs = extract_model_kwargs_from_request(request)

    model_request = {"input": prepared_input, **model_request_kwargs}

    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]
        if request.skill_args.get("average_adapters"):
            model_request["model_kwargs"]["average_adapters"] = True

    model_response = square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model response:\n{model_response}")

    return QueryOutput.from_question_answering(
        questions=query, model_api_output=model_response, context=context
    )
