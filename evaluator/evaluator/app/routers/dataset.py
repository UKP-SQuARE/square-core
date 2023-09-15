import logging
from typing import Dict, List

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from square_auth.auth import Auth

from evaluator.app import mongo_client
from evaluator.app.auth_utils import validate_access
from evaluator.app.core.dataset_handler import DatasetHandler
from evaluator.app.core.dataset_metadata import (
    DatasetMetadataDoesNotExistError,
    get_dataset_metadata,
)
from evaluator.app.core.task_helper import dataset_name_exists, metric_exists
from evaluator.app.models import SUPPORTED_SKILL_TYPES, DatasetMetadata

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset")
auth = Auth()


@router.get(
    "",
    response_model=List[DatasetMetadata],
)
async def get_datasets():
    """Returns a list of supported data sets."""

    results = mongo_client.client.evaluator.datasets.find()
    datasets = [DatasetMetadata.from_mongo(result) for result in results]
    logger.debug("get_datasets {datasets}".format(datasets=datasets))
    return datasets


@router.get("/{dataset_name}", status_code=200, response_model=DatasetMetadata)
async def get_dataset(dataset_name: str):
    try:
        return get_dataset_metadata(dataset_name)
    except DatasetMetadataDoesNotExistError as error:
        raise HTTPException(404, error.args)


@router.post(
    "",
    status_code=201,
)
async def create_metadata(
    request: Request,
    background_tasks: BackgroundTasks,
    dataset_metadata: DatasetMetadata = Body(
        examples={
            "extractive-qa": {
                "summary": "Extractive QA dataset mapping",
                "value": {
                    "name": "quoref",
                    "skill_type": "extractive-qa",
                    "metric": "squad",
                    "mapping": {
                        "id_column": "id",
                        "question_column": "question",
                        "context_column": "context",
                        "answers_column": "answers.text",
                    },
                },
            },
            "multiple-choice": {
                "summary": "Multiple Choice dataset mapping",
                "value": {
                    "name": "commonsense_qa",
                    "skill_type": "multiple-choice",
                    "metric": "exact_match",
                    "mapping": {
                        "id_column": "id",
                        "question_column": "question",
                        "choices_columns": ["choices.text"],
                        "choices_key_mapping_column": "choices.label",
                        "answer_index_column": "answerKey",
                    },
                },
            },
        }
    ),
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token_payload: Dict = Depends(auth),
):
    validate_access(token_payload)
    validate_dataset_name(dataset_metadata.name)
    await validate_mapping_and_skill_type(dataset_metadata)
    validate_metric(dataset_metadata.metric)

    logger.info(f"Creating new metadata: {dataset_metadata}")

    dataset_names = [d.name for d in await get_datasets()]
    if dataset_metadata.name in dataset_names:
        message = f"Metadata entry with dataset_name={dataset_metadata.name} already exists! Please use the PUT method to update the entry."
        logger.warning(message)
        raise HTTPException(
            400,
            message,
        )
    result = mongo_client.client.evaluator.datasets.insert_one(dataset_metadata.mongo())
    if result.acknowledged:
        logger.info(
            f"Metadata entry with dataset_name={dataset_metadata.name} successfully created. Triggering download dataset task after HTTP response..."
        )
        background_tasks.add_task(
            trigger_download_dataset, dataset_handler, dataset_metadata.name
        )
        return
    else:
        raise RuntimeError(result.raw_result)


@router.put(
    "",
    status_code=201,
)
async def update_metadata(
    request: Request,
    background_tasks: BackgroundTasks,
    dataset_metadata: DatasetMetadata = Body(
        examples={
            "extractive-qa": {
                "summary": "Extractive QA dataset mapping",
                "value": {
                    "name": "quoref",
                    "skill_type": "extractive-qa",
                    "metric": "squad",
                    "mapping": {
                        "id_column": "id",
                        "question_column": "question",
                        "context_column": "context",
                        "answers_column": "answers.text",
                    },
                },
            },
            "multiple-choice": {
                "summary": "Multiple Choice dataset mapping",
                "value": {
                    "name": "commonsense_qa",
                    "skill_type": "multiple-choice",
                    "metric": "exact_match",
                    "mapping": {
                        "id_column": "id",
                        "question_column": "question",
                        "choices_columns": ["choices.text"],
                        "choices_key_mapping_column": "choices.label",
                        "answer_index_column": "answerKey",
                    },
                },
            },
        }
    ),
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token_payload: Dict = Depends(auth),
):
    validate_access(token_payload)
    validate_dataset_name(dataset_metadata.name)
    await validate_mapping_and_skill_type(dataset_metadata)
    validate_metric(dataset_metadata.metric)

    logger.info(f"Updating metadata: {dataset_metadata}")

    dataset_names = [d.name for d in await get_datasets()]
    if dataset_metadata.name not in dataset_names:
        message = f"Metadata entry with dataset_name={dataset_metadata.name} does not exist! Please use the POST method to create the entry."
        logger.warning(message)
        raise HTTPException(
            400,
            message,
        )
    result = mongo_client.client.evaluator.datasets.replace_one(
        {"name": dataset_metadata.name}, dataset_metadata.mongo(), upsert=False
    )
    if result.acknowledged:
        logger.info(
            f"Metadata entry with dataset_name={dataset_metadata.name} successfully updated. Triggering re-download dataset task after HTTP response..."
        )
        background_tasks.add_task(
            trigger_download_dataset, dataset_handler, dataset_metadata.name
        )
        return
    else:
        raise RuntimeError(result.raw_result)


@router.delete(
    "/metadata/{dataset_name}",
    status_code=200,
)
async def delete_metadata(
    dataset_name: str,
    background_tasks: BackgroundTasks,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token_payload: Dict = Depends(auth),
):
    validate_access(token_payload)
    logger.debug(f"Deleting metadata with name: {dataset_name}")

    delete_result = mongo_client.client.evaluator.datasets.delete_one(
        {"name": dataset_name}
    )
    if delete_result.deleted_count == 1:
        logger.info(
            f"Metadata entry with dataset_name={dataset_name} successfully deleted. Triggering delete dataset task after HTTP response..."
        )
        background_tasks.add_task(trigger_delete_dataset, dataset_handler, dataset_name)
        return
    else:
        message = (
            f"Dataset {dataset_name} could not be deleted, because it was not found."
        )
        logger.warning(message)
        raise HTTPException(404, message)


async def validate_mapping_and_skill_type(dataset_metadata: DatasetMetadata):
    """
    Function that checks if the specified skill type exists and if the given mapping has the format of the skill type.
    """
    if dataset_metadata.skill_type not in SUPPORTED_SKILL_TYPES.keys():
        raise HTTPException(
            400,
            f'Skill type {dataset_metadata.skill_type} not supported! Please use one of the following skill types: {", ".join(SUPPORTED_SKILL_TYPES.keys())}',
        )
    try:
        SUPPORTED_SKILL_TYPES[dataset_metadata.skill_type].parse_obj(
            dataset_metadata.mapping
        )
    except ValidationError as error:
        raise HTTPException(
            400,
            f"The mapping does not match the skill type {dataset_metadata.skill_type}: {error.errors}",
        )


def validate_metric(metric: str):
    if metric_exists(metric) == False:
        raise HTTPException(
            400,
            f"Metric {metric} could not be found.",
        )


def validate_dataset_name(dataset_name: str):
    if dataset_name_exists(dataset_name) == False:
        raise HTTPException(
            400,
            f"Dataset {dataset_name} could not be found.",
        )


def trigger_download_dataset(dataset_handler: DatasetHandler, dataset_name: str):
    dataset_handler.download_dataset(dataset_name)


def trigger_delete_dataset(dataset_handler: DatasetHandler, dataset_name: str):
    dataset_handler.remove_dataset(dataset_name)
