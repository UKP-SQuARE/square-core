from fastapi import APIRouter

from evaluator.app.routers.dataset import router as dataset_router

router = APIRouter()

router.include_router(dataset_router)
