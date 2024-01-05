from fastapi import APIRouter

from profile_manager.routers.profile import router as profile_router

router = APIRouter()

router.include_router(profile_router)
