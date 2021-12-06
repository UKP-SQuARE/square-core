import logging
import uuid

from square_skill_api.models.prediction import QueryOutput
from square_skill_api.models.request import QueryRequest

from square_skill_helpers.config import SquareSkillHelpersConfig
from square_skill_helpers.square_api import ModelAPI

logger = logging.getLogger(__name__)

config = SquareSkillHelpersConfig.from_dotenv()
model_api = ModelAPI(config)

async def predict(request: QueryRequest) -> QueryOutput:
    """
    Process a given query and create the predictions for it.
    :param request: The user query
    :return: The prediction produced by the skill
    """
    context = request.skill_args["context"]
    # Call Model API
    prepared_input = [[request.query, context]]  # Change as needed
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {"topk": 10},
        "adapter_name": "qa/squad2@ukp"
    }

    output = await model_api(
        model_name="bert-base-uncased", 
        pipeline="question-answering", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{output}")
    # Prepare prediction
    query_output = []
    for ans in output["answers"][0]:
        if not ans["answer"]:
            continue

        prediction_score = ans["score"]

        prediction_output = {
            "output": ans["answer"],  # Set based on output
            "output_score": prediction_score
        }

        prediction_documents = [{
            "index": "",
            "document_id": "",
            "document": context,
            "span": [ans["start"], ans["end"]],
            "source": "",
            "url": ""
        }]  # Change as needed

        # Return
        prediction = {
            "prediction_score": prediction_score,
            "prediction_output": prediction_output,
            "prediction_documents": prediction_documents
        }
        query_output.append(prediction)

    # Answer for no answer
    if len(query_output) == 0:
        prediction = {
            "prediction_score": max(ans[0]["score"] for ans in output["answers"]),
            "prediction_output": {
                "output": "No answer found in the searched documents",
                "output_score": max(ans[0]["score"] for ans in output["answers"])
            },
            "prediction_documents": [{
                "index": "",
                "document_id": "",
                "document": context,
                "span": [0, 0],
                "source": "",
                "url": ""
            }]
        }
        query_output.append(prediction)

    return QueryOutput(predictions=query_output)
