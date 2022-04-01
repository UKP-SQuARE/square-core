from pydantic import BaseModel

class Task(BaseModel):
    message: str
    task_id: str
    task_state: str