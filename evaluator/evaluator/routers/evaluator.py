import datetime
import logging
from typing import Dict, List

import evaluate
from bson import ObjectId
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from square_auth.auth import Auth
from square_skill_api.models import PredictionOutput

from evaluator import mongo_client
from evaluator.core import DatasetHandler
from evaluator.core.dataset_handler import DatasetDoesNotExistError
from evaluator.models import DatasetResult, Metric
from evaluator.prediction_formatters import PredictionFormatter
from evaluator.routers import client_credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluator")
auth = Auth()


@router.post(
    "/{skill_id}/{dataset_name}/{metric_name}",
    status_code=201,
)
async def evaluatee(
    _request: Request,
    skill_id: str,
    dataset_name: str,
    metric_name: str,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    _token: str = Depends(client_credentials),
    _token_payload: Dict = Depends(auth),
):
    logger.debug(
        f"start evaluation with parameters: skill_id={skill_id}; dataset_name={dataset_name}; metric_name={metric_name}"
    )

    if metric_name != "squad_v2":
        logger.debug("Unsupported metric name!")
        raise HTTPException(
            400, "Sorry, we currently only support the metric 'squad_v2'!"
        )

    object_identifier = {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}

    try:
        metric = evaluate.load(metric_name)
    except FileNotFoundError:
        logger.debug(f"Metric with name='{metric_name}' not found!")
        raise HTTPException(404, f"Metric with name='{metric_name}' not found!")

    try:
        loaded_data = DatasetResult.from_mongo(
            mongo_client.client.evaluator.results.find_one(object_identifier)
        ).dict()
        logger.debug(f"Data loaded: {loaded_data}")
    except AttributeError:
        logger.debug(
            f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!"
        )
        raise HTTPException(
            404,
            f"Predictions for skill_id='{skill_id}' and dataset_name='{dataset_name}' not found!",
        )

    references = [
        {
            "answers": {
                "text": d["reference_answers"]["text"],
                "answer_start": d["reference_answers"]["answer_start"],
            },
            "id": d["id"],
        }
        for d in loaded_data["predictions"]
    ]
    logger.debug(f"Parsed references: {references}")

    predictions = [
        {
            "prediction_text": d["prediction"]["text"],
            "no_answer_probability": d["prediction"]["no_answer_probability"],
            "id": d["id"],
        }
        for d in loaded_data["predictions"]
    ]
    logger.debug(f"Parsed predictions: {predictions}")

    start_time = datetime.datetime.now()
    m = metric.compute(predictions=predictions, references=references)
    calculation_time = (datetime.datetime.now() - start_time).total_seconds()

    compute_metric(skill_id, dataset_name, metric_name)

    logger.debug(f"Metric in {calculation_time} seconds calculated: {m}")

    new_metrics = loaded_data["metrics"]
    new_metrics[metric_name] = Metric(
        metric_last_updated_at=datetime.datetime.now(),
        metric_calculation_time=calculation_time,
        results=m,
    ).dict()

    mongo_client.client.evaluator.results.update_one(
        object_identifier,
        {"$set": {"metrics": new_metrics}},
    )

    return DatasetResult.from_mongo(
        mongo_client.client.evaluator.results.find_one(object_identifier)
    )


def change_pred_format(prediction):
    logger.debug(prediction)
    tmp = {}
    tmp["id"] = prediction["id"]
    tmp["prediction"] = PredictionOutput(
        output=prediction["prediction"]["text"],
        output_score=(1 - prediction["prediction"]["no_answer_probability"]),
    )
    return tmp


@router.post(
    "/bene/{skill_id}/{dataset_name}/{metric_name}",
    status_code=201,
)
def compute_metric(
    skill_id: str,
    dataset_name: str,
    metric_name: str,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
):
    # get dataset metadata
    dataset_metadata = {
        "name": dataset_name,
        "skill-type": "extractive-qa",
        "mapping": {
            "id-column": "id",
            "question-column": "question",
            "context-column": "context",
            "answer-column": "answers",
        },
    }
    # get dataset
    dataset = dataset_handler.get_dataset(dataset_name)

    drop = dataset_handler.get_dataset("squad")
    logger.debug("squad")
    dataset_formatted = map_extractive_dataset(
        {
            "name": "drop",
            "skill-type": "extractive-qa",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
                "answer-start-column": "answers.answer_start",
            },
        },
        drop,
    )

    drop = dataset_handler.get_dataset("quoref")
    logger.debug("QUOREF")
    dataset_formatted = map_extractive_dataset(
        {
            "name": "quoref",
            "skill-type": "extractive-qa",
            "mapping": {
                "id-column": "id",
                "question-column": "question",
                "context-column": "context",
                "answer-text-column": "answers.text",
                "answer-start-column": "answers.answer_start",
            },
        },
        drop,
    )
    """
    # get metric
    metric = evaluate.load(metric_name)
    # get predictions of the skill on the dataset
    data = DatasetResult.from_mongo(
        mongo_client.client.evaluator.results.find_one({
            "skill_id": ObjectId(skill_id), 
            "dataset_name": dataset_name
        })
    ).dict()
    data["predictions"] = list(map(change_pred_format, data["predictions"]))
    # map predictions into correct format (from skill output format to metric format)
    predictions = PredictionFormatter().format(metric_name, data["predictions"])
    # map references into correct format (from dataset format to metric format)
    references = format_references(metric_name, dataset_metadata, dataset)

    try:
        computed_metric = metric.compute(predictions=predictions, references=references)
    except Exception as e:
        logger.error(f"Error while computing '{metric_name}' metric on '{dataset_name}' dataset: {e}")
        raise HTTPException(400, f"Error while computing '{metric_name}' metric on '{dataset_name}' dataset: {e}")

    logger.debug(computed_metric)
    return computed_metric
    """


def format_references(metric_name, dataset_metadata, dataset):
    if dataset_metadata["skill-type"] not in ["extractive-qa", "multiple-choice"]:
        skill_type = dataset_metadata["skill-type"]
        raise HTTPException(
            400, f"Evaluation of '{skill_type}' datasets is currently not supported."
        )

    if dataset_metadata["skill-type"] == "extractive-qa":
        # rename required columns
        dataset = dataset.rename_columns(
            {
                dataset_metadata["mapping"]["id-column"]: "id",
                dataset_metadata["mapping"]["answer-column"]: "answers",
            }
        )
        # remove unneccessary columns
        remove = list(set(dataset.column_names) - set(["id", "answers"]))
        dataset = dataset.remove_columns(remove)
    elif dataset_metadata["skill-type"] == "multiple-choice":
        dataset = dataset.map(quail_map)

    return [
        dataset[0],
        dataset[1],
        dataset[2],
        dataset[3],
        dataset[4],
        dataset[5],
        dataset[6],
        dataset[7],
    ]


def quail_map(sample):
    answer_index = sample["correct_answer_id"]
    sample["answer"] = sample["answers"][answer_index]
    return sample


def quartz_map(sample):
    answer_index = sample["choices"]["label"].index(sample["answerKey"])
    sample["answer"] = sample["choices"]["text"][answer_index]
    return sample


class ExtractiveDatasetSampleAnswer:
    def __init__(self):
        self.text = None
        self.answer_start = None

    def __str__(self):
        return f"text: '{self.text}', answer_start: '{self.answer_start}'"


class ExtractiveDatasetSample:
    def __init__(self):
        self.id = None
        self.question = None
        self.answers = []

    def __str__(self):
        answs = ""
        for ans in self.answers:
            answs += str(ans)
        return f"id: '{self.id}', question: '{self.question}', answers: [{answs}]"


def map_extractive_dataset(dataset_metadata, dataset):
    for sample in dataset:
        d = ExtractiveDatasetSample()
        d.id = sample[dataset_metadata["mapping"]["id-column"]]
        d.question = sample[dataset_metadata["mapping"]["question-column"]]

        attrs = dataset_metadata["mapping"]["answer-text-column"].split(".")
        answer_texts = sample[attrs[0]]
        if len(attrs) > 1:
            answer_texts = sample[attrs[0]][attrs[1]]

        try:
            attrs = dataset_metadata["mapping"]["answer-start-column"].split(".")
            answer_starts = sample[attrs[0]]
            if len(attrs) > 1:
                answer_starts = sample[attrs[0]][attrs[1]]
        except KeyError:
            answer_starts = False

        for answer_index, _ in enumerate(answer_texts):
            a = ExtractiveDatasetSampleAnswer()
            a.text = answer_texts[answer_index]
            if not answer_starts:
                a.answer_start = sample[
                    dataset_metadata["mapping"]["context-column"]
                ].index(a.text)
            else:
                a.answer_start = answer_starts[answer_index]
            d.answers.append(a)

        logger.debug(d)
