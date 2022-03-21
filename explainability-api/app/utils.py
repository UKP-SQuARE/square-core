import json
from app.models import Skill
import requests
import json
import os

# different types of question answering models
skill_types =[
    "span-extraction",
    "multiple-choice",
    "categorical"
]

# name of the files containing test cases for different types of question answering models
test_files = [
    "extractive_model_tests.json",
    "multiple_choice_model_tests.json",
    "boolean_model_tests.json"
]


def create_type_to_file():
    """ Creates a dictionary 

    Creates a dictionary where the key is the skill type and value is the file name 

    Returns:
        type_to_file (dict) : A dictionary containing all skill types and their corresponding files containing
            the test cases

    """
    type_to_file = dict()
    for i in range(len(skill_types)):
        type_to_file[skill_types[i]] = test_files[i]
    return type_to_file


def get_file_path(path ,skill_type):
    """ Creates the full path for the file

    Creates the directory path for the file

    Args:
        path (str) : Containing the directory
        skill_type : Type of the skill

    Returns:
        file_path (str) : full path of the file

    """
    type_to_file = create_type_to_file()
    file_name = type_to_file[skill_type]
    file_path = path + file_name
    return file_path


def get_json_data(path, skill_type):
    """ Function to get json data

    Creates a json object of the test cases contained in a file

    Args:
        path (str) : Containing the directory
        skill_type : Type of the skill

    Returns:
        json_data (json_object) : A json object containing all the test cases for a specific skill type

    """
    file_path = get_file_path(path, skill_type)
    json_file = open(file_path)
    json_data = json.load(json_file)
    return json_data


def create_query(test_case, capability, model, adapter):
    """ Create query

    This function query creates a query and make it suitable for sending to for prediction

    Args:
        test_case (dict) : Test case as a dictionary
        capability (str) : Capability of the given test case
        model (str) : Name of the language model
        adapter (str) : Name of the adapter

    Returns:
        json_object (json object) : A json object containing the test case and its prediction
        answer (str) : Prediction for test case made by the skill 

    """
    # initialize dictionary to contain context, name of the base model and adapter
    skill_args = dict()
    # initialize dictionary to contain a test case in suitable format for querying
    query = dict()

    # in case of multiple choice models add the options to the context seperated by \n otherwise context
    # will remain the same
    if "options" in test_case.keys():
        context = test_case['context']
        for option in test_case["options"]:
            context = context + "\n" + option
        skill_args["context"] = context
    else:
        skill_args["context"] = test_case['context']

    skill_args["base_model"] = model
    skill_args["adapter"] = adapter
    # skill args will be part of the query dictionary
    query["query"] = test_case['question']
    query["num_results"] = 1
    query["user_id"] = "ukp"

    query["skill_args"] = skill_args
    json_object = json.dumps(query)

    # get the original answer for the test case
    if "answer" not in test_case.keys():
        answer = test_case["prediction_before_change"]
    else:
        answer = test_case["answer"]

    return json_object, answer


def predict(skill_query_path, json_query, answer):
    """ Predicts a given query

    This function predicts a query and returns the prediction

    Args:
        skill_query_path (str) : Request path to query a skill
        json_query (json object) : Query as a json object

    Returns:
        Returns the prediction

    """
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(skill_query_path, data=json_query, headers=headers)
        predictions = response.json()
        prediction = predictions["predictions"][0]["prediction_output"]["output"]

        if answer == prediction:
            return "success"
        else:
            return "failed"

    except Exception as ex:
        print(ex)
        return "failed"


def save_json(json_data, path: str):
    """ Save a json object

    Saves a json object to a specific directory

    Args:
        json_data (json_object) : Containing all the test cases and their predictions
        path (str) : Full path of the directory where the json object will be saved

    """
    with open(path, 'w') as f:
        json.dump(json_data, f, indent=4)


def run_tests(skill: Skill, path: str):
    """ Function to run all the test cases for a given skill

    This function run all the test cases for a given skill

    Args:
        skill (Skill object) : A object of Skill containing all the information for a skill
        path (path) : Directory of the json file containing test cases for that skill type

    Returns:
        json_data (json object) : A json object containing all the test cases and their predictions for the given skill

    """
    
    json_data = get_json_data(path, skill.skill_type)
    num_tests = len(json_data['tests'])
    for i in range(num_tests):
        num_test_cases = len(json_data['tests'][i]['test_cases'])
        capability = json_data['tests'][i]['capability']
        success = 0
        failed = 0
        for j in range(num_test_cases):
            test_case = json_data['tests'][i]['test_cases'][j]
            json_query, answer = create_query(test_case, capability, skill.skill_base_model, skill.skill_adapter)
            result = predict(skill.skill_query_path, json_query, answer)
            json_data['tests'][i]['test_cases'][j]['success_failed'] = result
            if result == "success":
                success = success + 1
            else:
                failed = failed + 1
        total_cases = json_data['tests'][i]['total_cases']
        failure_rate = (failed / total_cases) * 100
        failure_rate_ = "{:.2f}".format(failure_rate)
        failure_rate = float(failure_rate_)
        success_rate = 100 - failure_rate
        json_data['tests'][i]["failed_cases"] = failed
        json_data['tests'][i]["success_cases"] = success
        json_data['tests'][i]["failure_rate"] = failure_rate
        json_data['tests'][i]["success_rate"] = success_rate
    return json_data


def create_file_paths(skill_id):
    """Get the directory

    This function creates and return the directory of the json file containing the test cases

    Args:
        skill_id (str) : ID of the skill
    
    Returns:
        test_file_path (str) : Directory of the file containing the test cases
    
    """
    base_dir = os.getcwd()  # os.path.normpath(os.getcwd() + os.sep + os.pardir)
    test_file_path = base_dir + "/model-tests/"
    # prediction_file_path = current_dir + "/predictions/" + skill_id + ".json"
    return test_file_path
