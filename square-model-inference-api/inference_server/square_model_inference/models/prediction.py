from pydantic import BaseModel

class AsyncTaskResult(BaseModel):
    message: str
    task_id: str
