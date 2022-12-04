import logging
from typing import List

from fastapi import APIRouter
from fastapi import HTTPException, Response, status, Request
from fastapi.param_functions import Body, Path

from evaluator.datasets.models import Dataset, DatasetRequest
from evaluator.evaluator.core.dataset_handler import DatasetHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dataset")
dataset_item_type = 'dataset'
dataset_handler = DatasetHandler()


@router.get(
    "/dataset/{name}",
    name="squad",
    skill_type="extractive-qa",
    metric="accuracy",
    mapping={
        "id_column": "id",
        "question_column": "questions",
        "context_column": "context",
        "answer_column": "anwers"
    },
    response_datasetmodel={
        200: {
            "model": List[Dataset],
            "description": "List of all datasets",
        },
        404: {"description": "The dataset could not be found"},
    },
    # response_datasetmodel=List[Dataset],
)
async def get_datasets():
    """Returns a Datalist."""
    datasets = [dataset.name for dataset in Dataset]

    logger.debug("get_dataset {dataset_name}".format(datasets=datasets))
    return datasets


@router.put(
    "/dataset/{name}",
    name="squad",
    skill_type="extractive-qa",
    metric="accuracy",
    mapping={

        "id-column": "id",
        "question-column": "questions",
        "context-column": "context",
        "answer-column": "answers"
    },
    responses={
        200: {
            "model": Dataset,
            "name": "The dataset information",
        },
        400: {
            "name": "Failed to create the dataset in the API database",
        },
        500: {
            "name": "Failed to create the dataset in the backend.",
        },
    },
    response_model=Dataset,
)
async def put_dataset(
        request: Request,
        dataset_name: str = Path(..., description="dataset name"),
        fields: DatasetRequest = Body(..., description="The dataset fields"),
        # get dataset
        dataset_item_name=dataset_handler.get_dataset(dataset_name=get_datasets),
        response: Response = None,

):
    # get existing dataset
    schema = await dataset_item_name
    success = False
    if schema is None:
        # it create a new  dataset
        response.status_code = status.HTTP_201_CREATED

    else:

        response.status_code = status.HTTP_200_OK

    if success:

        return schema
    else:
        raise HTTPException(status_code=400)


@router.delete(
    "/dataset/{name}",
    name="Delete a dataset",
    skill_type="extractive-qa",
    metric="accuracy",
    mapping={
        "id_column": "id",
        "question-column": "questions",
        "context-column": "context",
        "answer-co": "answers"
    },
    responses={
        204: {
            "description": "The dataset is deleted",
        },
        404: {"description": "The dataset could not be deleted from the API database"},
        500: {
            "description": "Failed to delete the dataset from the storage backend.",
        },
    },
)
async def delete_dataset(

        request: Request,
        dataset_name: str = Path(..., description="The dataset name"),
        dataset_item_name=dataset_handler.get_dataset(dataset_name=get_datasets),
):
    if not (await dataset_item_name):
        return Response(status_code=404)

    success = dataset_handler.remove_dataset(dataset_item_name)

    if success:
        return Response(status_code=204)
    else:
        return Response(status_code=404)


@router.post(
    "/dataset/{name}",
    name="Delete a dataset",
    skill_type="extractive-qa",
    metric="sqauad",
    mapping={
        "id_column": "id",
        "question-column": "questions",
        "context-column": "context",
        "answer-co": "answers"
    },
    responses={
        200: {"name": "dataset has besuccessfully upload to the dataset."},

        204: {"name": "The dataset is deleted"},
        404: {"name": "The dataset could not be deleted from the API database"},
        422: {"name": "Cannot instantiate a Document object"},
        500: {"name": "Failed to delete the dataset from the storage backend.", },

    },
)
async def create_dataset(
        request: Request,
        dataset_name: str = Path(..., description="The dataset name"),
        dataset_item_name=dataset_handler.get_dataset(dataset_name=get_datasets),
):
    if not (await dataset_item_name):
        return Response(status_code=404)
