from fastapi import APIRouter

from square_skill_api.api.routes import heartbeat, query

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(query.router, tags=["query"])
