from fastapi import APIRouter

from evaluator.routers.example import router as example_router
from evaluator.routers.evaluator import router as evaluator_router

router = APIRouter()

router.include_router(example_router)
router.include_router(evaluator_router)
