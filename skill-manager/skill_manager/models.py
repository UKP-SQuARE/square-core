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


class SkillInputExample(BaseModel):
    query: str
    context: Optional[str]
    answers: Optional[List[str]]


class Skill(MongoModel):
    id: Optional[PyObjectId]
    name: str
    url: str
    skill_type: SkillType
    skill_settings: SkillSettings
    skill_input_examples: Optional[List[SkillInputExample]]
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    description: str = None
    default_skill_args: Dict = None
    published: bool = False

    @validator("url")
    def validate_url(cls, url):
        if not url.startswith("http"):
            raise ValueError(url)
        if url.endswith("/"):
            url = url[:-1]
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
                    "requires_multiple_choices": 0,
                },
                "default_skill_args": {},
                "user_id": "Dave",
                "published": False,
                "skill_input_examples": [
                    {
                        "query": "What arms did Moonwatchers band carry?",
                        "context": "At the water's edge, Moonwatcher and his band stop. They carry their bone clubs and bone knives. Led by One-ear, the Others half-heartly resume the battle-chant. But they are suddenly confrunted with a vision that cuts the sound from their throats, and strikes terror into their hearts.",
                    }
                ],
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
