from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from profile_manager.mongo.mongo_model import MongoModel
from profile_manager.mongo.py_object_id import PyObjectId

from pydantic import BaseModel
from typing import List, Optional

class Badge(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    type: str

class Submission(BaseModel):
    id: str
    date: str
    llmName: str

class Certificate(BaseModel):
    id: str
    title: str
    studentName: str
    score: str
    evaluationType: str
    issueDate: str
