from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
    )
import requests
from app.routers import utils

router = APIRouter()


@router.put("/run-checklist", name="run-checklist")
async def run_checklist_tests(skill_name, test_type, capability):
    """ Function for testing a Skill

    Takes an input of Skill class object and returns a json consisting
    all the test cases and their prediction made by the specified skill

    Args:
        skill (Skill) : An object of class Skill
        test_type: can be one of MFT and INV
        capability: can be one of Vocabulary, Taxonomy, Robustness, NER, Temporal, Negation, Fairness, Coref, SRL

    Returns:
        json_data (json object) : A json object containing all the test cases and their predictions made by
            the specified skill

    """
    # path = create_file_paths(skill.skill_id)
    # json_data = run_tests(skill, path)

    # TODO
    # get tests based on the skill name, test type and capability
    skill_info = requests.get(url='https://square.ukp-lab.de/api/skill-manager/skill')
    print(skill_info)

    # create the request format for prediction

    # get prediction

    # add test results to db

    return ""


@router.put("/add-tests-to-db", name="add checklist tests")
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
    result = await utils.process_json(data)
    return result
