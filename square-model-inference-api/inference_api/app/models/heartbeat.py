from pydantic import BaseModel


class HeartbeatResult(BaseModel):
    is_alive: bool
