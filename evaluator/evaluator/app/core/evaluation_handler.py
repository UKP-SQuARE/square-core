import logging
import os

from bson import ObjectId

from evaluator.app import mongo_client
from evaluator.app.core.dataset_metadata import get_dataset_metadata
from evaluator.app.core.task_helper import (
    dataset_exists,
    metric_exists,
    skill_exists,
    task_id,
)
from evaluator.app.models import Evaluation, EvaluationStatus, PredictionResult
from evaluator.tasks import evaluate_task, predict_task

logger = logging.getLogger(__name__)
QUEUE = os.getenv("QUEUE", "evaluation")


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
    ) -> Evaluation:
        logger.info(
            f"User '{user_id}' requested evaluation of skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}'."
        )

        # choose default metric if no metric was specified
        if metric_name is None:
            metadata = get_dataset_metadata(dataset_name)
            metric_name = metadata.metric
            logger.info(f"Going to use default metric '{metric_name}' for evaluation.")

        evaluation = Evaluation(
            user_id=user_id,
            skill_id=ObjectId(skill_id),
            dataset_name=dataset_name,
            metric_name=metric_name,
            prediction_status=EvaluationStatus.requested,
            metric_status=EvaluationStatus.requested,
            prediction_error=None,
            metric_error=None,
        )

        # check if metric/predictions are already computed (or already requested)
        predictions_already_computed = self.check_predictions_already_computed(
            skill_id, dataset_name
        )
        metric_already_computed = self.check_metric_already_computed(
            skill_id, dataset_name, metric_name
        )

        if predictions_already_computed and metric_already_computed:
            logger.info(
                f"Evaluation for skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}' already exists."
            )
            return Evaluation.from_mongo(
                mongo_client.client.evaluator.evaluations.find_one(
                    {
                        "skill_id": ObjectId(skill_id),
                        "dataset_name": dataset_name,
                        "metric_name": metric_name,
                    }
                )
            )

        if not predictions_already_computed:
            # calculate predictions and then (re-)compute the metric
            self.do_predictions(user_id, token, skill_id, dataset_name, metric_name)
        elif not metric_already_computed:
            # only calculate the metric
            evaluation.prediction_status = EvaluationStatus.finished
            self.compute_metric(user_id, token, skill_id, dataset_name, metric_name)

        id = mongo_client.client.evaluator.evaluations.replace_one(
            {
                "user_id": user_id,
                "skill_id": ObjectId(skill_id),
                "dataset_name": dataset_name,
                "metric_name": metric_name,
            },
            evaluation.mongo(),
            upsert=True,
        ).upserted_id

        return self.get(id)

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

        self.perform_pre_checks(token, skill_id, dataset_name, metric_name)

        task = predict_task.predict.apply_async(
            args=(skill_id, dataset_name, metric_name, token),
            task_id=task_id("predict", skill_id, dataset_name),
            queue=QUEUE,
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

        self.perform_pre_checks(token, skill_id, dataset_name, metric_name)

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
            queue=QUEUE,
        )
        logger.info(
            f"Created evaluation-task for skill '{skill_id}' on dataset '{dataset_name}' and metric '{metric_name}'. Task-ID: '{task.id}'"
        )

        return task.id

    def perform_pre_checks(
        self, token: str, skill_id: str, dataset_name: str, metric_name: str = None
    ):
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

    def get(self, id: str) -> Evaluation:
        return Evaluation.from_mongo(
            mongo_client.client.evaluator.evaluations.find_one({"_id": id})
        )

    def check_predictions_already_computed(
        self, skill_id: str, dataset_name: str
    ) -> bool:
        return self.check_already_computed(
            {"skill_id": ObjectId(skill_id), "dataset_name": dataset_name}
        )

    def check_metric_already_computed(
        self, skill_id: str, dataset_name: str, metric_name: str
    ) -> bool:
        return self.check_already_computed(
            {
                "skill_id": ObjectId(skill_id),
                "dataset_name": dataset_name,
                "metric_name": metric_name,
            }
        )

    def check_already_computed(self, filter):
        existing = Evaluation.from_mongo(
            mongo_client.client.evaluator.evaluations.find_one(filter)
        )
        if existing is not None:
            status = (
                existing.metric_status
                if "metric_name" in filter
                else existing.prediction_status
            )
            return not status == EvaluationStatus.failed
        return False
