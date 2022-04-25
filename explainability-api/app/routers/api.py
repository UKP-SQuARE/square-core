from fastapi import APIRouter

from app.routers import heartbeat, checklist

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(checklist.router, tags=["checklist"], prefix="/checklist")
# api_router.include_router(run_checklist_celery.router, tags=["celery-task"], prefix="/celery")
# api_router.include_router(celery_result.router, tags=["celery-result"], prefix="/celery")
