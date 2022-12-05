from fastapi import APIRouter

from evaluator.app.routers.dataset import router as dataset_router
from evaluator.app.routers.evaluator import router as evaluator_router
from evaluator.app.routers.predictor import router as predictor_router

router = APIRouter()

router.include_router(dataset_router)
router.include_router(evaluator_router)
router.include_router(predictor_router)
