from pydantic import BaseModel, Field
from beanie import Document
from fastapi.security import HTTPBasicCredentials


class ChecklistTests(Document):
    qa_type: str
    test_type: str
    capability: str
    test_name: str
    test_name_description: str
    test_type_description: str
    capability_description: str
    test_cases: list

    class Collection:
        name = "checklist_tests"

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdul@youngest.dev",
                "password": "3xt3m#"
            }
        }


class TaskGenericModel(BaseModel):
    """Celery generic task representation"""

    message: str = Field(..., description="Error or success message")
    task_id: str = Field(..., description="id of the task being processed by celery")


class TaskResultModel(BaseModel):
    """Celery task response"""

    task_id: str = Field(..., description="id of the task being processed by celery")
    status: str = Field(..., description="status of the celery task being processed")
    result: dict = Field(..., description="the response from the requested endpoint")
