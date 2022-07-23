import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question and context, performs extractive QA using an adapter trained on
    SQuADV2.0.
    """
    context = request.skill_args["context"]
    explain_kwargs = request.skill_args.get("explain_kwargs", {})

    prepared_input = [[request.query, context]]  # Change as needed
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {"topk": 10},
        "adapter_name": "qa/squad2@ukp",
        "explain_kwargs": explain_kwargs,
    }

    model_api_output = await model_api(
        model_name="bert-base-uncased",
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_question_answering(
        model_api_output=model_api_output, context=context
    )
