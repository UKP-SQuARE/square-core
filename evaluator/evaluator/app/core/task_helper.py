import logging
import os

import requests
from evaluate import list_evaluation_modules

from datasets import list_datasets
from evaluator.app.core.dataset_metadata import get_dataset_metadata

logger = logging.getLogger(__name__)
skill_manager_url = os.getenv(
    "SKILL_MANAGER_API_URL", "https://square.ukp-lab.de/api/skill-manager"
)


def task_id(task_name, skill_id, dataset_name, metric_name=None) -> str:
    """
    Generates a task id.

    Args:
        task_name (str): Name of the task.
        skill_id (str): ID of the skill.
        dataset_name (str): Name of the dataset.
        metric_name (str): Optional name of a metric.

    Returns: Task id.
    """
    task_id = f"{task_name}-{skill_id}-{dataset_name}"
    if metric_name is not None:
        task_id = f"{task_id}-{metric_name}"
    return task_id


def skill_exists(skill_id, token) -> bool:
    """
    Checks if the given skill exists.

    Args:
        skill_id (str): ID of the skill.
        token (str): Authentication token. Required for non-public skills.

    Returns: True if the skill exists. Otherwise False.
    """
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{skill_manager_url}/skill/{skill_id}",
        headers=headers,
        timeout=30,
    )

    return response.status_code == 200


def dataset_name_exists(dataset_name: str) -> bool:
    """
    Checks if the dataset name exists in Huggingface.

    Args:
        dataset_name (str): Name of the dataset.

    Returns: True if the dataset exists. Otherwise False.
    """
    return dataset_name in list_datasets()


def dataset_exists(dataset_name) -> bool:
    """
    Checks if the dataset entry exists in the SQuARE project.

    Args:
        dataset_name (str): Name of the dataset.

    Returns: True if the dataset exists. Otherwise False.
    """
    try:
        dataset_metadata = get_dataset_metadata(dataset_name)
    except Exception as e:
        logger.error(f"{e}")
        return False
    return dataset_metadata is not None


def metric_exists(metric_name) -> bool:
    """
    Checks if the metric exists.

    Args:
        metric_name (str): Name of the metric.

    Returns: True if the metric exists. Otherwise False.
    """
    return metric_name in list_evaluation_modules()
