from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from square_skill_api.models.prediction import Prediction as SkillPrediction

from skill_manager.mongo_model import MongoModel
from skill_manager.py_object_id import PyObjectId


class SkillType(str, Enum):
    abstractive = "abstractive"
    span_extraction = "span-extraction"
    multiple_choiche = "multiple-choice"
    categorical = "categorical"
    open_domain = "open-domain"

class SkillSettings(BaseModel):
    requires_context: bool = False
    requires_multiple_choices: int = Field(0, ge=0)

class Skill(MongoModel):
    id: Optional[PyObjectId]
    name: str
    url: str
    skill_type: SkillType
    skill_settings: SkillSettings
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    description: str = None
    default_skill_args: Dict = None
    published: bool = False

    @validator("url")
    def validate_url(cls, url):
        if not url.startswith("http"): raise ValueError(url)
        if url.endswith("/"): url = url[:-1]
        return url

    class Config:
        schema_extra = {
            "example": {
                "name": "HAL9000",
                "url": "http://h.al:9000",
                "description": "Heuristically programmed Algorithmic computer",
                "skill_type": "abstractive",
                "skill_settings": {
                    "requires_context": False,
                    "requires_multiple_choices": 0
                },
                "default_skill_args": {},
                "user_id": "Dave",
                "created_at": "1992-01-12T09:00:00.000000",
                "published": False
            }
        }

class Prediction(MongoModel):
    id: Optional[PyObjectId]
    skill_id: PyObjectId
    skill_name: str
    query: str
    query_time: datetime = Field(default_factory=datetime.now)
    user_id: str
    predictions: List[SkillPrediction]
