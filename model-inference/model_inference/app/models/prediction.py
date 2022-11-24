from pydantic import BaseModel


class AsyncTaskResult(BaseModel):
    """Async task result model."""

    message: str
    task_id: str
