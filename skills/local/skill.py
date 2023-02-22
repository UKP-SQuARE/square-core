import logging

from square_datastore_client import SQuAREDatastoreClient
from square_model_client import SQuAREModelClient
from square_skill_api.models import (
    Prediction,
    PredictionOutput,
    QueryOutput,
    QueryRequest,
)

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
square_datastore_client = SQuAREDatastoreClient()


async def predict(request: QueryRequest) -> QueryOutput:
    return QueryOutput(
        predictions=[
            Prediction(
                question="What is the capital of France?",
                prediction_score=0.9,
                prediction_output=PredictionOutput(output="Paris", output_score=0.9),
            )
        ]
    )
