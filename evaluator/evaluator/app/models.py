from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from evaluator.app.mongo.mongo_model import MongoModel
from evaluator.app.mongo.py_object_id import PyObjectId


class DataSet(str, Enum):
    """Enum for different data sets."""

    CommonSenseQA = "CommonSenseQA"
    CosmosQA = "CosmosQA"
    DROP = "DROP"
    HotpotQA = "HotpotQA"
    MultiRC = "MultiRC"
    NarrativeQA = "NarrativeQA"
    NewsQA = "NewsQA"
    OpenBioASQ = "OpenBioASQ"
    QuAIL = "QuAIL"
    QuaRTz = "QuaRTz"
    Quoref = "Quoref"
    RACE = "RACE"
    SQuAD = "SQuAD"
    Social_IQA = "Social-IQA"
    BoolQ = "BoolQ"
