from pydantic import BaseModel, Field


class TaskGenericModel(BaseModel):
    """Celery generic task representation"""

    message: str = Field(..., description="Error or success message")
    task_id: str = Field(..., description="id of the task being processed by celery")


class TaskResultModel(BaseModel):
    """Celery task response"""

    task_id: str = Field(..., description="id of the task being processed by celery")
    status: str = Field(..., description="status of the celery task being processed")
    result: dict = Field(..., description="the response from the requested endpoint")
