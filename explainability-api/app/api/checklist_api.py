from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
    )

import logging
import requests

from app.explainers import checklist
from app.db import mongo_operations
from app.core.config import settings
from app.models.celery import (
    TaskGenericModel,
    TaskResultModel
)

from celery.result import AsyncResult
from starlette.responses import JSONResponse

from tasks import tasks

logger = logging.getLogger(__name__)

router = APIRouter()
database = mongo_operations.Database()


@router.put("/results", name="run-checklist", response_model=TaskGenericModel)
async def run_checklist_tests(skill_id: str):
    """ Function for testing a Skill

    Takes an input of Skill class object and returns a json consisting
    all the test cases and their prediction made by the specified skill

    Args:
        skill_id (Skill) : id of the skill for which the checklist has to be run
        # capability: can be one of Vocabulary, Taxonomy, Robustness, NER, Temporal, Negation, Fairness, Coref, SRL

    Returns:
        json_data (json object) : A json object containing all the test cases and their predictions made by
            the specified skill

    """
    # TODO
    # get tests based on the skill

    try:
        skill_info = requests.get(url=f"{settings.API_URL}/api/skill-manager/skill")
        # print(skill_info.json())
        skill = [skill for skill in skill_info.json() if skill_id == skill["id"]][0]
        result = tasks.run_checklist.delay(skill)
        # logger.info(result)
        return {
            "message": f"Queued running checklist on skill: {skill_id}",
            "task_id": result.id
        }
    except Exception as e:
        logger.info("Could not execute the task and got error:", e)
        return {
            "message": f"Could not queue checklist task for skill: {skill_id}. "
                       f"Exception: {e}",
            "task_id": ""
        }


@router.put("/tests", name="add checklist tests")
async def add_checklist_tests(file: UploadFile = File(...)):
    """
    request format
    {
        "qa_type": "categorical",
        "tests": [
        {
        "test_type": "MFT",
        "capability": "Vocabulary",
        "test_name": "A is COMP than B. Who is more / less COMP??",
        "test_name_description": "Compare person A and person B with different comparative adjective
            and test's models ability to understand the comparative words",
        "test_type_description": "MFT stands for Minimum Functionality Test. This testing type is
            inspired from unit testing of software engineering. For this type of testing precise and
            small testing datasets are created and the models are tested on that particular test set.
            MFTs are useful particularly for detecting when models use alternative approaches to handle
            complicated inputs without actually knowing the inside out of the capability. For MFT test
            cases, labeled test set is required.",
        "capability_description": "This capability tests whether a model has necessary vocabulary and whether
            it has the ability to handle the importance of different words.",
        "test_cases": [
                    {
                        "context": "Caroline is nicer than Marie.",
                        "question": "Is Caroline less nice?",
                        "answer": "no"
                    },
                    {
                        "context": "Caroline is nicer than Marie.",
                        "question": "Is Caroline nicer than Marie?",
                        "answer": "yes"
                    },
                ]
        }
    }
    """
    # check file type
    if file.content_type != "application/json":
        raise HTTPException(status_code=415, detail="Unsupported file format. Please upload a json file.")
    data = await file.read()
    # process data to extract tests and add them to db
    result = await checklist.process_data(data)
    return result


@router.get("/task/{task_id}",
            name="task-status",
            response_model=TaskResultModel)
async def get_task_status(task_id):
    """
    Get results from a celery task
    """
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={"task_id": str(task_id), "status": "Processing", "result": {}})
    result = task.get()
    return {
        "task_id": str(task_id),
        "status": "Finished",
        "result": result
    }
