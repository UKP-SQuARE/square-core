from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from evaluator.mongo.mongo_model import MongoModel
from evaluator.mongo.py_object_id import PyObjectId


class DataSet(str, Enum):
    """Enum for different data sets."""

    BoolQ = "boolq"
    CommonSenseQA = "commonsense_qa"
    CosmosQA = "cosmos_qa"
    DROP = "drop"
    DuoRC = "duorc"
    HotpotQA = "hotpot_qa"
    HellaSWAG = "hellaswag"
    HybridQA = "hybrid_qa"
    MultiRC = "eraser_multi_rc"
    NarrativeQA = "narrativeqa"
    NaturalQuestions = "natural_questions"
    NewsQA = "newsqa"
    OpenBioASQ = "OpenBioASQ"
    QuAIL = "quail"
    QAMR = "biu-nlp/qamr"
    QuaRTz = "quartz"
    Quoref = "quoref"
    RACE = "race"
    SearchQA = "search_qa"
    Social_IQA = "social_i_qa"
    SQuAD = "squad"
    TriviaQA = "trivia_qa"
