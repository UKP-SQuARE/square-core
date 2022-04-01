from fastapi import APIRouter

from api.routes import heartbeat, run_checklist, run_checklist_celery, celery_result

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(run_checklist.router, tags=["checklist"], prefix="/checklist")
api_router.include_router(run_checklist_celery.router, tags=["celery-task"], prefix="/celery")
api_router.include_router(celery_result.router, tags=["celery-result"], prefix="/celery")


