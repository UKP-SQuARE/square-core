import logging
from typing import List

from fastapi import APIRouter

from evaluator.app.models import DataSet

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leaderboard")


@router.get(
    "/{dataset_name}/{metric_name}",
    response_model=List,
)
async def get_leaderboard(dataset_name: str, metric_name: str):
    leaderboard = [
        {
            "rank": 5,
            "date": "2022-12-23",
            "skill_name": "OpenBioASQ: BM25+Roberta-SQuAD",
            "result": {"exact_match": 90.39, "f1": 95.53},
        },
        {
            "rank": 2,
            "date": "2022-12-12",
            "skill_name": "dl4nlp/distilbert-base-uncased-nq-short-for-square v2",
            "result": {"exact_match": 83.1, "f1": 92.53},
        },
        {
            "rank": 3,
            "date": "2022-12-01",
            "skill_name": "QuAIL RoBERTa Adapter",
            "result": {"exact_match": 89.75, "f1": 91.53},
        },
        {
            "rank": 4,
            "date": "2022-12-06",
            "skill_name": "SpanBert - NaturalQuestionsShort",
            "result": {"exact_match": 89.55, "f1": 90.53},
        },
    ]
    return leaderboard
