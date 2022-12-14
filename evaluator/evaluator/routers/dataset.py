import logging
from typing import Dict, List

from bson import ObjectId
from evaluate import load
from fastapi import APIRouter, Depends, HTTPException, Request
from square_auth.auth import Auth

from evaluator import mongo_client
from evaluator.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler
from evaluator.models import Dataset, DatasetResult
from evaluator.mongo.mongo_client import MongoClient
from evaluator.routers import client_credentials
from evaluator.routers.evaluator import get_dataset_metadata

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset")
dataset_item_type = "dataset"
dataset_handler = DatasetHandler()

auth = Auth()


@router.post(
    "/{dataset_name}/{skill_type}/{metric}",
    status_code=200,
)
async def create_dataset(
    request: Request,
    dataset_name: str,
    skill_type: str,
    metric: str,
    mapping: dict,
    dataset_handler: DatasetHandler = Depends(DatasetHandler),
    token: str = Depends(client_credentials),
    token_payload: Dict = Depends(auth),
    validate: bool = False,
):
    logger.debug(
        f"post dataset: dataset_name= {dataset_name}; skill_type = {skill_type}; metric = {metric}"
    )

    metadata = get_dataset_metadata(dataset_name=dataset_name)
    logger.debug(f"dataset_item : {metadata}")

    # validate item
    if skill_type == metadata["skill-type"] and metric == metadata["metric"]:
        validate = True
        logger.info(f"dataset_name {metadata['name']}")

        dataset_name = metadata["name"]
        skill_type = metadata["skill-type"]
        metric = metadata["metric"]
        mapping = metadata["mapping"]
        mapping["id-column"] = metadata["mapping"]["id-column"]
        mapping["question-column"] = metadata["mapping"]["question-column"]

        if metadata["name"] == "quoref":
            mapping["context-column"] = metadata["mapping"]["context-column"]
            mapping["answer-text-column"] = metadata["mapping"]["answer-text-column"]

        elif metadata["name"] == "commonsense_qa":
            mapping["choices-columns"] = metadata["mapping"]["choices-columns"]
            mapping["choices-key-mapping-column"] = metadata["mapping"][
                "choices-key-mapping-column"
            ]
            mapping["answer-index-column"] = metadata["mapping"]["answer-index-column"]
        else:
            logger.debug(f"undefined dataset_name={dataset_name}")

    else:
        logger.debug(f"Dataset doest not exist!")

    if validate:
        # database object
        dataset_ob = Dataset(
            dataset_name=dataset_name,
            skill_type=skill_type,
            metric=metric,
            mapping=mapping,
        )
        # Check if the dataset_name exist on mongodb
        dataset_name_exist = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )

        if dataset_name_exist is None:
            if str(dataset_ob.dataset_name) == str("commonsense_qa"):
                dataset_mapping = {
                    "dataset_name": dataset_ob.dataset_name,
                    "skill-type": dataset_ob.skill_type,
                    "metric": dataset_ob.metric,
                    "mapping": {
                        "id-column": dataset_ob.mapping["id-column"],
                        "question-column": dataset_ob.mapping["question-column"],
                        "choices-columns": dataset_ob.mapping["choices-columns"],
                        "choices-key-mapping-column": dataset_ob.mapping[
                            "choices-key-mapping-column"
                        ],
                        "answer-index-column": dataset_ob.mapping[
                            "answer-index-column"
                        ],
                    },
                }
                mongo_client.client.evaluator.datasets.insert_one(dataset_mapping)
                return dataset_mapping
        elif str(dataset_ob.dataset_name) == str("quoref"):
            dataset_mapping = {
                "dataset_name": dataset_ob.dataset_name,
                "skill-type": dataset_ob.skill_type,
                "metric": dataset_ob.metric,
                "mapping": {
                    "id-column": dataset_ob.mapping["id-column"],
                    "question-column": dataset_ob.mapping["question-column"],
                    "context-column": dataset_ob.mapping["context-column"],
                    "answer-text-column": dataset_ob.mapping["answer-text-column"],
                },
            }
            mongo_client.client.evaluator.datasets.insert_one(dataset_mapping)
            return dataset_mapping
        else:
            return f"{dataset_ob.dataset_name} is not a valid dataset_name"
    else:
        return "Dataset exist on collection datasets"
    return metadata


@router.get(
    "/{dataset_name}",
    status_code=200,
)
async def get_dataset(
    dataset_name: str,
):
    # get the database
    # get collection and find dataset_name on the collection

    logger.debug(f"GET dataset: dataset_name= {dataset_name}")
    try:
        db_dataset_name = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )
        if db_dataset_name is not None:
            logger.debug(f"Dataset_name exist on datasets collection!")
            for item in db_dataset_name:

                if str(item["dataset_name"]) == str("commonsense_qa"):

                    return {
                        "dataset_name": item["dataset_name"],
                        "skill-type": item["skill-type"],
                        "metric": item["metric"],
                        "mapping": {
                            "id-column": item["mapping"]["id-column"],
                            "question-column": item["mapping"]["question-column"],
                            "choices-columns": item["mapping"]["choices-columns"],
                            "choices-key-mapping-column": item["mapping"][
                                "choices-key-mapping-column"
                            ],
                            "answer-index-column": item["mapping"][
                                "answer-index-column"
                            ],
                        },
                    }
                elif str(item["dataset_name"]) == str("quoref"):
                    return {
                        "dataset_name": item["dataset_name"],
                        "skill-type": item["skill-type"],
                        "metric": item["metric"],
                        "mapping": {
                            "id-column": item["mapping"]["id-column"],
                            "question-column": item["mapping"]["question-column"],
                            "context-column": item["mapping"]["context-column"],
                            "answer-text-column": item["mapping"]["answer-text-column"],
                        },
                    }
                else:
                    return f" Undefined dataset_name"
        else:
            return "Dataset_name not exist on the datasets collection!"

    except DatasetDoesNotExistError:
        raise HTTPException(404, f"Dataset_name not found!")


@router.put(
    "/{dataset_name}/{skill_type}/{metric}",
    status_code=200,
)
async def put_dataset(dataset_name: str, skill_type: str, metric: str):
    logger.debug("put dataset")
    metadata = get_dataset_metadata(dataset_name=dataset_name)

    # check if the dataset_name exist on the collection mongodb
    try:
        dataset_result = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )
    except DatasetDoesNotExist:
        logger.error(msg)
        raise HTTPException(400)

    for dataset_item in dataset_result:
        if dataset_item["dataset_name"] is not None:
            try:
                myquery = {"dataset_name": dataset_item["dataset_name"]}
                new_value = {"$set": {"skill-type": skill_type, "metric": metric}}
                mongo_client.client.evaluator.datasets.update_one(myquery, new_value)

                logger.debug(f"Dataset_name {dataset_name} is updated from mongodb!")
                return f"Dataset_name: {dataset_item['dataset_name']} has be update"
            except HTTPException:
                logger.error(msg)
                raise HTTPException(400, msg)
    return dataset_name


@router.delete(
    "/{dataset_name}",
    status_code=200,
)
async def delete_dataset(dataset_name: str):
    logger.debug("Delete dataset_name on mongodb")

    # check if dataset_name exist on the database
    try:
        result_db = mongo_client.client.evaluator.datasets.find(
            {"dataset_name": dataset_name}
        )
        logger.debug(f"db_dataser_name = {result_db}")
    except DatasetDoesNotExistError:
        logger.error(msg)
        raise HTTPException(404, msg)

    for item in result_db:
        if item["dataset_name"] is not None:

            try:
                mongo_client.client.evaluator.datasets.delete_one(
                    {"dataset_name": item["dataset_name"]}
                )
                logger.debug(
                    f"Dataset_name {item['dataset_name']} is deleted from mongodb!"
                )
            except DatasetDoesNotExistError:
                logger.error(msg)
                raise HTTPException(404, msg)
            return f"dataset_name: {item['dataset_name']} has be deleted!"

    return f"dataset_name: {dataset_name} not exist on the Database!"
