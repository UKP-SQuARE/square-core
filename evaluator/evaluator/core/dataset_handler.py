import logging
import os
from typing import Union

import datasets
from datasets import Dataset, DatasetDict, DownloadMode, Split
from evaluator.core.dataset_formatter import DatasetFormatter
from evaluator.settings import DatasetHandlerSettings

logger = logging.getLogger(__name__)


class DatasetDoesNotExistError(Exception):
    """Raised when a dataset is requested which does not exist either locally or on huggingface."""

    def __init__(self, dataset: str) -> None:
        msg = f'The requested dataset "{dataset}" does not exist locally and was not found on huggingface.'
        super().__init__(msg)


class DatasetHandler:
    def __init__(self) -> None:
        self.settings = DatasetHandlerSettings()
        self.dataset_formatter = DatasetFormatter()

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
            dataset = datasets.load_from_disk(self.settings.dataset_dir + dataset_name)
        except FileNotFoundError:
            logger.debug(
                f'Dataset "{dataset_name}" not found locally. Going to download it.'
            )
            try:
                dataset = self.download_dataset(dataset_name)
            except FileNotFoundError:
                raise DatasetDoesNotExistError(dataset_name)

        return dataset

    def remove_dataset(self, dataset_name: str) -> bool:
        """
        Deletes the specified dataset from local storage.

        Args:
            dataset_name (str): Name of the dataset on huggingface.

        Returns:
        :bool: True if the dataset-file was removed. False if it did not exist.
        """
        logger.info(f'Removing dataset "{dataset_name}" from local storage.')
        try:
            os.remove(self.settings.dataset_dir + dataset_name)
            return True
        except FileNotFoundError:
            return False

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
        dataset = datasets.load_dataset(
            dataset_name,
            split="validation[:8]",
            download_mode=DownloadMode.FORCE_REDOWNLOAD,
        )
        dataset.save_to_disk(self.settings.dataset_dir + dataset_name)
        return dataset

    def to_generic_format(self, dataset, dataset_metadata, sample_ids=None):
        """
        Formats the given dataset into an universal (per skill-type) format.

        Args:
            dataset (:class:`Dataset` or :class:`DatasetDict`:): Dataset from huggingface.
            dataset_metadata (dict): Metadata about the dataset.
            sample_ids (List[str]): Optional list of sample-ids. When specified, only samples with the respective ids will be returned.
                                    Otherwise all samples in the dataset will be returned.
                                    The returned samples will be in the same order as the passed sample-ids.

        Returns: List of samples in the dataset in an universal format depending on the datasets skill-type.
        """
        return self.dataset_formatter.format(dataset, dataset_metadata, sample_ids)
