import logging

from bson import ObjectId

from evaluator.app import mongo_client
from evaluator.app.core.task_helper import (
    dataset_exists,
    metric_exists,
    skill_exists,
    task_id,
)
from evaluator.app.models import PredictionResult, get_dataset_metadata
from evaluator.tasks import evaluate_task, predict_task

logger = logging.getLogger(__name__)


class EvaluationHandler:
    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        user_id: str,
        token: str,
        skill_id: str,
        dataset_name: str,
        metric_name: str = None,
    ):
        logger.info(
            f"User '{user_id}' requested evaluation of skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}'."
        )

        if metric_name is None:
            metadata = get_dataset_metadata(dataset_name)
            metric_name = metadata["metric"]
            logger.info(f"Going to use default metric '{metric_name}' for evaluation.")

        self.do_predictions(user_id, token, skill_id, dataset_name, metric_name)

    def do_predictions(
        self,
        user_id: str,
        token: str,
        skill_id: str,
        dataset_name: str,
        metric_name: str = None,
    ) -> str:
        logger.info(
            f"Requested prediction-task for skill '{skill_id}' on dataset '{dataset_name}' with metric '{metric_name}'"
        )

        # check if the skill exists
        if not skill_exists(skill_id, token):
            msg = f"Skill '{skill_id}' does not exist or you do not have access."
            logger.error(msg)
            raise ValueError(msg)

        # check if the dataset exists
        if not dataset_exists(dataset_name):
            msg = f"Dataset '{dataset_name}' does not exist."
            logger.error(msg)
            raise ValueError(msg)

        # check if the metric exists
        if (metric_name is not None) and (not metric_exists(metric_name)):
            msg = f"Metric '{metric_name}' does not exist."
            logger.error(msg)
            raise ValueError(msg)

        task = predict_task.predict.apply_async(
            args=(skill_id, dataset_name, metric_name, token),
            task_id=task_id("predict", skill_id, dataset_name),
        )
        logger.info(
            f"Created prediction-task for skill '{skill_id}' on dataset '{dataset_name}'. Task-ID: '{task.id}'"
        )

        return task.id

    def compute_metric(
        self,
        user_id: str,
        token: str,
        skill_id: str,
        dataset_name: str,
        metric_name: str,
    ) -> str:
        logger.info(
            f"Requested evaluation-task for skill '{skill_id}' on dataset '{dataset_name}' with metric '{metric_name}'"
        )

        # check if the skill exists
        if not skill_exists(skill_id, token):
            msg = f"Skill '{skill_id}' does not exist or you do not have access."
            logger.error(msg)
            raise ValueError(msg)

        # check if the dataset exists
        if not dataset_exists(dataset_name):
            msg = f"Dataset '{dataset_name}' does not exist."
            logger.error(msg)
            raise ValueError(msg)

        # check if the metric exists
        if not metric_exists(metric_name):
            msg = f"Metric '{metric_name}' does not exist."
            logger.error(msg)
            raise ValueError(msg)

        # check if predictions exist
        try:
            prediction_result = PredictionResult.from_mongo(
                mongo_client.client.evaluator.predictions.find_one(
                    {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}
                )
            )
            if prediction_result is None:
                raise AttributeError
        except AttributeError:
            msg = f"No predictions found for skill '{skill_id}' on dataset '{dataset_name}'. Make sure to run the prediction first before evaluating."
            logger.error(msg)
            raise ValueError(msg)

        task = evaluate_task.evaluate.apply_async(
            args=(skill_id, dataset_name, metric_name),
            task_id=task_id("evaluate", skill_id, dataset_name, metric_name),
        )
        logger.info(
            f"Created evaluation-task for skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}'. Task-ID: '{task.id}'"
        )

        return task.id
