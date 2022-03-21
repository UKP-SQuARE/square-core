from fastapi import FastAPI
from .models import Skill
from .utils import create_file_paths, run_tests

app = FastAPI()


@app.get("/")
async def check_health():
    """ Checks the health of the Explainability API

    Returns a message of about the health of the API

    """
    return "Api is running"


@app.post("/test")
async def test_skill(skill: Skill):
    """ Function for testing a Skill

    Takes an input of Skill class object and returns a json consisting 
    all the test cases and their prediction made by the specified skill

    Args:

        skill (Skill) : An object of class Skill
    
    Returns:

        json_data (json object) : A json object containing all the test cases and their predictions made by the specified skill

    """
  
    #get the file containing all the test cases
    test_file_path = create_file_paths(skill.skill_id)
    #run the test cases from the test file and get the json object
    json_data = run_tests(skill, test_file_path)
    
    return json_data



