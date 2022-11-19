import logging
import os
from typing import Union

from datasets import (
    Dataset,
    DatasetDict,
    DownloadMode,
    Split,
    load_dataset,
    load_from_disk,
)

logger = logging.getLogger(__name__)


class DatasetDoesNotExistError(Exception):
    """Raised when a dataset is requested which does not exist either locally or on huggingface."""

    def __init__(self, dataset: str) -> None:
        msg = "The requested dataset '{dataset}' does not exist locally and was not found on huggingface.".format(
            dataset=dataset
        )
        super().__init__(msg)


class DatasetHandler:
    def __init__(self) -> None:
        self.dataset_dir = "/app/datasets/"

    def get_dataset(self, dataset_name: str) -> Union[Dataset, DatasetDict]:
        """
        Retrieves the validation-set of the specified dataset.
        Datasets will always be loaded locally from disk if possible.
        If the dataset does not exist locally, it will be downloaded and saved.

        Args:
            dataset_name (str): Name of the dataset on huggingface.

        Returns:
        :class:`Dataset` or :class:`DatasetDict`:
        - If `dataset_name` is a path of a dataset directory: the dataset requested.
        - If `dataset_name` is a path of a dataset dict directory: a ``datasets.DatasetDict`` with each split.
        """
        try:
            dataset = load_from_disk(self.dataset_dir + dataset_name)
        except FileNotFoundError:
            logger.debug(
                "Dataset '{dataset}' not found locally. Going to download it.".format(
                    dataset=dataset_name
                )
            )
            try:
                dataset = self.download_dataset(dataset_name)
            except FileNotFoundError:
                raise DatasetDoesNotExistError(dataset_name)

        return dataset

    def remove_dataset(self, dataset_name: str):
        """
        Deletes the specified dataset from local storage.

        Args:
            dataset_name (str): Name of the dataset on huggingface.
        """
        logger.info(
            "Removing dataset '{dataset}' from local storage.".format(
                dataset=dataset_name
            )
        )
        os.remove(self.dataset_dir + dataset_name)

    def download_dataset(self, dataset_name: str) -> Union[Dataset, DatasetDict]:
        """
        (Re-)Downloads the validation-set of the specified dataset and saves it locally (even if it already exists locally).

        Args:
            dataset_name (str): Name of the dataset on huggingface.

        Returns:
        :class:`Dataset` or :class:`DatasetDict`:
        - If `dataset_name` is a path of a dataset directory: the dataset requested.
        - If `dataset_name` is a path of a dataset dict directory: a ``datasets.DatasetDict`` with each split.
        """
        dataset = load_dataset(
            dataset_name,
            split=Split.VALIDATION,
            download_mode=DownloadMode.FORCE_REDOWNLOAD,
        )
        dataset.save_to_disk(self.dataset_dir + dataset_name)
        return dataset
