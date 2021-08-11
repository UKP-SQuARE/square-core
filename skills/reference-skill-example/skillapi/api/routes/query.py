from fastapi import APIRouter
from starlette.requests import Request

from skillapi.models.request import QueryRequest
from skillapi.models.prediction import QueryOutput
from skillapi.skill import predict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryOutput, name="Skill Query")
async def query(query: QueryRequest) -> QueryOutput:
    logger.info(f"Query: {query.dict()}")
    prediction = await predict(query)

    return prediction
