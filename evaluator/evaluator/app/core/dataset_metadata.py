import logging

from evaluator.app import mongo_client
from evaluator.app.models import DatasetMetadata

logger = logging.getLogger(__name__)


class DatasetMetadataDoesNotExistError(Exception):
    """Raised when a dataset metadata is requested which does not exist."""

    def __init__(self, dataset: str) -> None:
        msg = f'The requested dataset metadata "{dataset}" does not exist.'
        super().__init__(msg)


def get_dataset_metadata(dataset_name: str):
    """
    Function to retrieve the metadata for the specified `dataset_name`.

    If no metadata is found, we raise `DatasetMetadataDoesNotExistError`.
    """
    dataset_metadata = DatasetMetadata.from_mongo(
        mongo_client.client.evaluator.datasets.find_one({"name": dataset_name})
    )
    if dataset_metadata is None:
        raise DatasetMetadataDoesNotExistError(dataset_name)

    logger.info(f"METADATA: {dataset_metadata}")
    return dataset_metadata
