import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and a set of answer candidates, predicts the most likely answer."""

    answers = request.skill_args.get("choices")
    if answers is None:
        answers = request.skill_args["context"].split("\n")

    prepared_input = [[request.query, c] for c in answers]
    model_request = {
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "adapter_name": "AdapterHub/bert-base-uncased-pf-commonsense_qa",
    }
    model_api_output = await model_api(
        model_name="bert-base-uncased",
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_sequence_classification(
        answers=answers, model_api_output=model_api_output
    )
