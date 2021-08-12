from fastapi import APIRouter

from square_model_inference.api.routes import heartbeat, prediction

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(prediction.router, tags=["prediction"])
