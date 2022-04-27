import logging
import asyncio

from .celery_app import app
from fastapi.exceptions import HTTPException
from app.explainers import checklist
from app.db import mongo_operations

from abc import ABC

from celery import Task

logger = logging.getLogger(__name__)


class ExplainerTask(Task, ABC):
    """
    Abstraction of Celery's Task class to support providing mongo client.
    """

    abstract = True

    def __init__(self):
        super().__init__()
        self.client = None
        self.credentials = None

    def __call__(self, *args, **kwargs):
        """
        Instantiate mongo client on first call (i.e. first task processed)
        Avoids the creation of multiple clients for each task request
        """
        if not self.client:
            logging.info("Instantiating Mongo Client...")
            self.client = mongo_operations.Database()

        # if not self.credentials:
        #     self.credentials = client_credentials
        return self.run(*args, **kwargs)


@app.task(
    bind=True,
    base=ExplainerTask,
    name="run-checklist",
          )
def run_checklist(self, skill):
    """
    Run the checklist tests on the input skill
    """
    try:
        self.client.server_info()
    except Exception:
        return {"success": False, "message": "Connection to the database failed."}

    skill_id = skill["id"]
    skill_type = skill["skill_type"]

    try:
        # get tests from db
        test_cases = self.client.get_tests_from_db(qa_type=skill_type)
        # create the request format for prediction
        if test_cases:
            model_inputs = checklist.create_query(skill, test_cases)
            # get predictions
            model_outputs = checklist.predict(model_inputs, skill_id)
            # add results to db
            status = asyncio.run(self.client.add_results_to_db(skill_id, model_outputs))
            if status:
                return {
                    "success": status,
                    "message": "Checklist tests were run and results were saved to the db."
                }
            else:
                return {
                    "success": status,
                    "message": "Checklist tests could not be saved to the db. Please check if they already exist."
                }
        else:
            logger.info("No tests retrieved for the specified qa_type")
            raise HTTPException(status_code=400, detail="No test cases were retrieved from the db for"
                                                        "the particular skill")

    except Exception as e:
        logger.info("Caught exception. %s ", e)
        return {"success": False, "message": f"exited with error: {e}"}
