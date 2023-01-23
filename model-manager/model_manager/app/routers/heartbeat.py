from fastapi import APIRouter

from model_manager.app.models.heartbeat import HeartbeatResult


router = APIRouter()


@router.get("/heartbeat", response_model=HeartbeatResult, name="heartbeat")
def get_heartbeat() -> HeartbeatResult:
    heartbeat = HeartbeatResult(is_alive=True)
    return heartbeat
