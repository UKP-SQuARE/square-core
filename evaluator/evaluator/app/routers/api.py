from fastapi import APIRouter

from evaluator.app.routers.dataset import router as dataset_router
from evaluator.app.routers.evaluations import router as evaluations_router
from evaluator.app.routers.leaderboard import router as leaderboard_router
from evaluator.app.routers.evaluation import router as evaluation_router
from evaluator.app.routers.task import router as task_router

router = APIRouter()

router.include_router(dataset_router)
router.include_router(task_router)
router.include_router(leaderboard_router)
router.include_router(evaluations_router)
router.include_router(evaluation_router)
