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
    query = request.query
    context = request.skill_args.get("context")
    answers = request.skill_args["answers"]

    adapter = request.skill_args["adapter"]
    base_model = request.skill_args["base_model"]

    if context is not None:
        prepared_input = [[context, query + " " + answer] for answer in answers]
    else:
        prepared_input = [[query, answer] for answer in answers]

    # Call Model API
    model_request = {  # Fill as needed
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "adapter_name": adapter
    }

    output = await model_api(
        model_name=base_model, 
        pipeline="sequence-classification", 
        model_request=model_request
    )
    logger.info(f"Model API output:\n{output}")

    # Prepare prediction
    query_output = []
    for i in range(len(answers)):
        logit = output["model_outputs"]["logits"][0][i]
        prediction_score = logit

        prediction_output = {
            "output": answers[i], 
            "output_score": logit
        }

        prediction_documents = [{
            "index": "",
            "document_id": "",
            "document": "",
            # "span": ["", ""],
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

    query_output = sorted(query_output, key=lambda item: item["prediction_score"], reverse=True)

    return QueryOutput(predictions=query_output)
