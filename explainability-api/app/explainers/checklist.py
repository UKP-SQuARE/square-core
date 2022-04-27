# add functionality to process json to be injected into the db
import json
import logging
import requests
import itertools

from collections import OrderedDict

from app.models.skill import Skill
from app.db.mongo_operations import Database
from app.core.config import settings

from typing import List

logger = logging.getLogger(__name__)

mongo_client = Database()


##################################################################
#                   CHECKLIST FUNCTIONS                          #
##################################################################


async def process_data(data: bytes):
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
        skill: input skill for which the checklist tests are run
        test_cases (list) : Test cases as a list

    Returns:
        json_object (json object) : A json object containing the test case and its prediction
        answer (str) : Prediction for test case made by the skill

    """
    skill_type = skill["skill_type"]
    base_model = skill["default_skill_args"].get("base_model")
    adapter = skill["default_skill_args"].get("adapter")
    # extract all tests
    all_tests = [tests["test_cases"] for tests in test_cases]
    # all_tests = list(itertools.chain.from_iterable([tests["test_cases"] for tests in test_cases]))
    questions, contexts, answers = list(), list(), list()

    test_type = list(itertools.chain.from_iterable([[test["test_type"]] * len(test["test_cases"])
                                                    for test in test_cases]))
    capability = list(itertools.chain.from_iterable([[test["capability"]] * len(test["test_cases"])
                                                    for test in test_cases]))
    test_name = list(itertools.chain.from_iterable([[test["test_name"]] * len(test["test_cases"])
                                                    for test in test_cases]))

    for tests in all_tests:
        questions.append([query["question"] for query in tests])
        # list of list for mcq else list
        contexts.append([query["context"] if skill_type != "multiple-choice" else [query["context"] + "\n" + option
                        for option in query["options"]] for query in tests])
        answers.extend([query.get("answer") if "answer" in query.keys() else query.get("prediction_before_change")
                        for query in tests])

        # TODO
        # send batch to the skill query endpoint

    prediction_requests = list()
    # create the prediction request
    for idx in range(len(questions)):
        for question, context in zip(questions[idx], contexts[idx]):
            request = dict()
            request["num_results"] = 1
            request["user_id"] = "ukp"
            request["skill_args"] = {"base_model": base_model, "adapter": adapter,"context": context}
            request["query"] = question
            prediction_requests.append(request)

    model_inputs = dict()
    model_inputs["request"] = prediction_requests
    model_inputs["answers"] = answers
    model_inputs["test_type"] = test_type
    model_inputs["capability"] = capability
    model_inputs["test_name"] = test_name

    return model_inputs


def predict(model_inputs: dict, skill_id: str):
    """ Predicts a given query

    This function predicts a query and returns the prediction

    Args:
        model_inputs (dict) : input for the model inference
        skill_id (str) : id of skill for which the predictions need to be run

    Returns:
        Returns the model predictions and success rate
    """
    model_outputs = list()
    try:
        headers = {'Content-type': 'application/json'}
        skill_query_url = f"{settings.API_URL}/api/skill-manager/skill/{skill_id}/query"
        model_predictions = list()
        i = 0
        for request in model_inputs["request"]:
            response = requests.post(skill_query_url, data=json.dumps(request), headers=headers)
            predictions = response.json()
            model_predictions.append(predictions["predictions"][0]["prediction_output"]["output"])
            i += 1
            if i == 2:
                break
        # print(model_predictions)
        # print(model_inputs)
        # print(model_inputs["answers"][0])

        # calculate success rate
        success_rate = [pred == gold for pred, gold in zip(model_predictions, model_inputs["answers"])]

        for test_type, capability, test_name, request, answer, prediction, success in zip(
            model_inputs["test_type"],
            model_inputs["capability"],
            model_inputs["test_name"],
            model_inputs["request"],
            model_inputs["answers"],
            model_predictions,
            success_rate
        ):
            model_outputs.append(
                {
                    "test_type": test_type,
                    "capability": capability,
                    "test_name": test_name,
                    "question": request["query"],
                    "context": request["skill_args"]["context"],
                    "answer": answer,
                    "prediction": prediction,
                    "success": success
                }
            )
        # print(model_outputs)
    except Exception as ex:
        logger.info(ex)
    return model_outputs


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
