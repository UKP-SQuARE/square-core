# add functionality to process json to be injected into the db
import json
import requests
import itertools
from app.models.skill import Skill
from app.db.mongo_operations import Database

from typing import List


mongo_client = Database()


##################################################################
#                   CHECKLIST FUNCTIONS                          #
##################################################################


async def process_json(data: bytes):
    """
    process json file consisting of tests for adding to the database
    """
    try:
        data = json.loads(data)
        env = dict()
        env["qa_type"] = data["qa_type"]
        results = list()
        for tests in data["tests"]:
            env["test_type"] = tests["test_type"]
            env["capability"] = tests["capability"]
            env["test_name"] = tests["test_name"]
            env["test_name_description"] = tests["test_name_description"]
            env["test_type_description"] = tests["test_type_description"]
            env["capability_description"] = tests["capability_description"]
            env["test_cases"] = tests["test_cases"]
            # add tests to db
            results.append(await mongo_client.add_tests_to_db(env))
        if False in results and True in results:
            return {
                "status": True,
                "message": "Duplicated tests were skipped"
            }
        elif False not in results:
            return {
                "status": True,
                "message": "All tests were added successfully"
            }
        elif True not in results:
            return {
                "status": False,
                "message": "None of the test cases were added. Please check if they have been already added."
            }

    except KeyError as e:
        message = f'error processing file: {e}'
        return {
            "status": False,
            "message": message
        }


def create_query(skill, test_cases: List):
    """
    Create query for prediction
    This function query creates a query and make it suitable for sending to for prediction

    Args:
        test_cases (list) : Test case as a list

    Returns:
        json_object (json object) : A json object containing the test case and its prediction
        answer (str) : Prediction for test case made by the skill

    """
    skill_type = skill["skill_type"]
    # initialize dictionary to contain context, name of the base model and adapter
    skill_args = dict()
    skill_args = skill["default_skill_args"]  # gets base model and adapter
    # initialize dictionary to contain a test case in suitable format for querying
    request = dict()
    request["num_results"] = 1
    request["user_id"] = "ukp"
    # extract all tests
    all_tests = [tests["test_cases"] for tests in test_cases]
    # all_tests = list(itertools.chain.from_iterable([tests["test_cases"] for tests in test_cases]))
    for tests in all_tests:
        questions = [query["question"] for query in tests]
        # list of list for mcq else list
        contexts = [query["context"] if skill_type != "multiple-choice" else [query["context"] + "\n" + option
                    for option in query["options"]] for query in tests]
        answers = [query.get("answer") if "answer" in query.keys() else query.get("prediction_before_change")
                   for query in tests]
        # print(answers)
        # send batch to the skill query endpoint

    # prediction_request = json.dumps(request)
    # # get the original answer for the test case
    # if "answer" not in test_case.keys():
    #     answer = test_case["prediction_before_change"]
    # else:
    #     answer = test_case["answer"]

    # return prediction_request, answer
#
#
# def predict(skill_query_path, json_query, answer):
#     """ Predicts a given query
#
#     This function predicts a query and returns the prediction
#
#     Args:
#         skill_query_path (str) : Request path to query a skill
#         json_query (json object) : Query as a json object
#
#     Returns:
#         Returns the prediction
#
#     """
#     try:
#         headers = {'Content-type': 'application/json'}
#         response = requests.post(skill_query_path, data=json_query, headers=headers)
#         predictions = response.json()
#         prediction = predictions["predictions"][0]["prediction_output"]["output"]
#
#         if answer == prediction:
#             return "success"
#         else:
#             return "failed"
#
#     except Exception as ex:
#         print(ex)
#         return "failed"
#
#
# def run_tests(skill: Skill, path: str):
#     """ Function to run all the test cases for a given skill
#
#     This function run all the test cases for a given skill
#
#     Args:
#         skill (Skill object) : A object of Skill containing all the information for a skill
#         path (path) : Directory of the json file containing test cases for that skill type
#
#     Returns:
#         json_data (json object) : A json object containing all the test cases and their
#           predictions for the given skill
#
#     """
#
#     json_data = get_json_data(path, skill.skill_type)
#     num_tests = len(json_data['tests'])
#     for i in range(num_tests):
#         num_test_cases = len(json_data['tests'][i]['test_cases'])
#         capability = json_data['tests'][i]['capability']
#         success = 0
#         failed = 0
#         for j in range(num_test_cases):
#             test_case = json_data['tests'][i]['test_cases'][j]
#             json_query, answer = create_query(test_case, capability, skill.skill_base_model, skill.skill_adapter)
#             result = predict(skill.skill_query_path, json_query, answer)
#             json_data['tests'][i]['test_cases'][j]['success_failed'] = result
#             if result == "success":
#                 success = success + 1
#             else:
#                 failed = failed + 1
#         total_cases = json_data['tests'][i]['total_cases']
#         failure_rate = (failed / total_cases) * 100
#         failure_rate_ = "{:.2f}".format(failure_rate)
#         failure_rate = float(failure_rate_)
#         success_rate = 100 - failure_rate
#         json_data['tests'][i]["failed_cases"] = failed
#         json_data['tests'][i]["success_cases"] = success
#         json_data['tests'][i]["failure_rate"] = failure_rate
#         json_data['tests'][i]["success_rate"] = success_rate
#     return json_data


##################################################################
#                   CHECKLIST FUNCTIONS END                      #
##################################################################
