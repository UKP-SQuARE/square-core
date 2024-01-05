from fastapi import APIRouter


##todo

###
#
#

from profile_manager.routers.dataset import router as dataset_router
from profile_manager.routers.health import router as health_router
from profile_manager.routers.skill import router as skill_router
from profile_manager.routers.skill_types import router as skill_types_router

router = APIRouter()

router.include_router(health_router)
router.include_router(skill_router)
router.include_router(skill_types_router)
router.include_router(dataset_router)
