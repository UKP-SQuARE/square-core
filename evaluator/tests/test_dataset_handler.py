import os
from unittest.mock import MagicMock

import pytest

import datasets
from evaluator.core.dataset_handler import DatasetDoesNotExistError, DatasetHandler


@pytest.fixture(scope="module")
def dataset_handler():
    return DatasetHandler()


@pytest.fixture(scope="module")
def dataset_name():
    return "dummy"


@pytest.fixture(scope="module")
def dataset_location(dataset_handler, dataset_name):
    return dataset_handler.settings.dataset_dir + dataset_name


def test_remove_dataset_deletes_file(dataset_handler, dataset_name, dataset_location):
    os.remove = MagicMock()
    removed = dataset_handler.remove_dataset(dataset_name)
    assert removed
    os.remove.assert_called_once_with(dataset_location)


def test_remove_dataset_does_not_fail_on_non_existing_dataset(
    dataset_handler, dataset_name, dataset_location
):
    os.remove = MagicMock(side_effect=FileNotFoundError())
    removed = dataset_handler.remove_dataset(dataset_name)
    assert not removed
    os.remove.assert_called_once_with(dataset_location)


def test_download_dataset_loads_and_then_saves_to_disk(
    dataset_handler, dataset_name, dataset_location
):
    dataset_mock = MagicMock()
    datasets.load_dataset = MagicMock(return_value=dataset_mock)
    datasets.save_to_disk = MagicMock(return_value=dataset_mock)

    returned_dataset = dataset_handler.download_dataset(dataset_name)

    assert returned_dataset == dataset_mock
    datasets.load_dataset.assert_called_once_with(
        dataset_name,
        split=datasets.Split.VALIDATION,
        download_mode=datasets.DownloadMode.FORCE_REDOWNLOAD,
    )
    dataset_mock.save_to_disk.assert_called_once_with(dataset_location)


def test_get_dataset_returns_local_dataset_if_exists(
    dataset_handler, dataset_name, dataset_location
):
    dataset_mock = MagicMock()
    datasets.load_from_disk = MagicMock(return_value=dataset_mock)
    dataset_handler.download_dataset = MagicMock()

    returned_dataset = dataset_handler.get_dataset(dataset_name)

    assert returned_dataset == dataset_mock
    datasets.load_from_disk.assert_called_once_with(dataset_location)
    dataset_handler.download_dataset.assert_not_called()


def test_get_dataset_downloads_dataset_if_not_exists_locally(
    dataset_handler, dataset_name, dataset_location
):
    dataset_mock = MagicMock()
    datasets.load_from_disk = MagicMock(side_effect=FileNotFoundError())
    dataset_handler.download_dataset = MagicMock(return_value=dataset_mock)

    returned_dataset = dataset_handler.get_dataset(dataset_name)

    assert returned_dataset == dataset_mock
    datasets.load_from_disk.assert_called_once_with(dataset_location)
    dataset_handler.download_dataset.assert_called_once_with(dataset_name)


def test_get_dataset_throws_error_if_dataset_not_found(
    dataset_handler, dataset_name, dataset_location
):
    dataset_mock = MagicMock()
    datasets.load_from_disk = MagicMock(side_effect=FileNotFoundError())
    dataset_handler.download_dataset = MagicMock(side_effect=FileNotFoundError())

    with pytest.raises(DatasetDoesNotExistError):
        returned_dataset = dataset_handler.get_dataset(dataset_name)

    datasets.load_from_disk.assert_called_once_with(dataset_location)
    dataset_handler.download_dataset.assert_called_once_with(dataset_name)
