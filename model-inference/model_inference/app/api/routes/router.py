from model_inference.app.api.routes import heartbeat, prediction
from fastapi import APIRouter


api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(prediction.router, tags=["prediction"])
