from fastapi import APIRouter
from starlette.requests import Request

from square_model_inference.models.request import PredictionRequest
from square_model_inference.models.prediction import PredictionOutput
from square_model_inference.inference.model import Model

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput, name="predict")
async def predict(
    request: Request,
    prediction_request: PredictionRequest = None,
) -> PredictionOutput:

    model: Model = request.app.state.model
    prediction: PredictionOutput = await model.predict(prediction_request)

    return prediction
