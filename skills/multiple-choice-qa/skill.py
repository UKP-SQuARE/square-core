import logging
import uuid

from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

from utils import extract_model_kwargs_from_request

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, a set of answers and optional context, performs multiple-choice
    QA. This skill is a general skill, it can be used with any adapter for
    multiple-choice question answering. The adapter to use can be specified in the
    `skill_args` or via the `default_skill_args` in the skill-manager.
    """
    query = request.query
    context = request.skill_args.get("context")
    choices = request.skill_args["choices"]

    if request.skill.get("skill_type") == "categorical":
        # answer choices for categorical skills are hard-coded and not required as
        # input.
        prepared_input = [[context, query]]
    else:
        if context is None:
            prepared_input = [[query, choice] for choice in choices]
        else:
            prepared_input = [[context, query + " " + choice] for choice in choices]

    model_request_kwargs = extract_model_kwargs_from_request(request)
    model_request = {
        "input": prepared_input,
        **model_request_kwargs,
    }
    if request.skill_args.get("adapter"):
        model_request["adapter_name"] = request.skill_args["adapter"]
        if request.skill_args.get("average_adapters"):
            model_request["model_kwargs"]["average_adapters"] = True

    logger.debug("Request for model api:{}".format(model_request))

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info("Model response: {}".format(model_response))

    if request.skill_args.get("multiple_answers", False):
        # if multiple answers can be correct, logits is a 2d array:
        # [[p1(false), p1(true)], ...]
        # we flatten this to [[p1(true), p2(true), ...]]

        # index of the logits to select for answer selection
        idx = request.skill_args.get("multiple_answers_idx", 1)
        model_response["model_outputs"]["logits"] = [
            [l[idx] for l in model_response["model_outputs"]["logits"]]
        ]

    return QueryOutput.from_sequence_classification(
        questions=query,
        answers=choices,
        model_api_output=model_response,
        context=context,
    )
