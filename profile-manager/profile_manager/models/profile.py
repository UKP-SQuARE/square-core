from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from profile_manager.mongo.mongo_model import MongoModel
from profile_manager.mongo.py_object_id import PyObjectId

from pydantic import BaseModel
from typing import List, Optional

class LLM(MongoModel):
    id: Optional[PyObjectId] = Field(None, description="Identifier generated by mongoDB")
    Name: str
    version: str

class Badge(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    title: str
    description: str
    icon: str
    type: str

class Certificate(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    title: str
    studentName: str
    score: str
    evaluationType: str
    issueDate: str

class Submission(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    date: str
    llmName: str

class Profile(MongoModel):
    id: Optional[PyObjectId] = Field(None, description="Identifier generated by mongoDB")
    email: str
    overallPoints: int
    currentPoints: int
    certificates: List[PyObjectId] = []    # Default to empty list
    badges: List[PyObjectId] = []          # Default to empty list
    submissions: List[PyObjectId] = []     # Default to empty list
    availableModels: List[PyObjectId] = [] # References to LLM models

