from pydantic import BaseModel


class HeartbeatResult(BaseModel):
    """Heartbeat result model."""

    is_alive: bool
