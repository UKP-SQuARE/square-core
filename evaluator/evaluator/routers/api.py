from fastapi import APIRouter

from evaluator.routers.example import router as example_router

router = APIRouter()

router.include_router(example_router)
