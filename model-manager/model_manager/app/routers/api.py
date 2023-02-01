from fastapi import APIRouter

from model_manager.app.routers import heartbeat, management


api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(management.router, tags=["model-management"])
