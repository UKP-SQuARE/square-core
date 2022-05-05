from pydantic import BaseModel, Field

class TaskStatus(BaseModel):
    task_id: str = Field(...)
    status: str = Field(...)

class TaskResult(BaseModel):
    task_id: str = Field(...)
    result: dict = Field(...)
