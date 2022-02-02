from pydantic import BaseModel, Field


class HeartbeatResult(BaseModel):
    is_alive: bool = Field(
        ..., description="`True` if Skill is up and running, else `False`"
    )
