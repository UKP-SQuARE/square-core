from fastapi import APIRouter

from app.api import heartbeat, attack_api , checklist_api

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(checklist_api.router, tags=["checklist"], prefix="/checklist")
api_router.include_router(attack_api.router, tags=["attack"], prefix="/attack")
