from pydantic import BaseModel, Field

class HeartbeatResult(BaseModel):
    is_alive: bool = Field(..., description="if the api is alive or not")
    
