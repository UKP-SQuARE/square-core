from app.models.heartbeat import HeartbeatResult
from fastapi import APIRouter


router = APIRouter()


@router.get("/heartbeat", response_model=HeartbeatResult, name="heartbeat")
def get_heartbeat() -> HeartbeatResult:
    heartbeat = HeartbeatResult(is_alive=True)
    return heartbeat
