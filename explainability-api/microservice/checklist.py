# add functionality to process json to be injected into the db
import json
import logging
import requests
import itertools

from typing import List


def create_query(skill, test_cases: List):
    """
    Creates a query and make it suitable for sending to for prediction

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
        contexts.append([query["context"] if skill_type != "multiple-choice"
                         else query["context"] + "\n" + "\n".join(query["options"])
                         for query in tests])
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
            request["skill_args"] = {"base_model": base_model, "adapter": adapter, "context": context}
            request["query"] = question
            prediction_requests.append(request)

    model_inputs = dict()
    model_inputs["request"] = prediction_requests
    model_inputs["answers"] = answers
    model_inputs["test_type"] = test_type
    model_inputs["capability"] = capability
    model_inputs["test_name"] = test_name
    # logger.info("inputs:", model_inputs)

    return model_inputs


def predict(model_inputs: dict, skill_id: str) -> list:
    """
    Predicts a given query

    Args:
        model_inputs (dict) : input for the model inference
        skill_id (str) : id of skill for which the predictions need to be run

    Returns:
        Returns the model predictions and success rate
    """
    model_outputs = list()
    try:
        headers = {'Content-type': 'application/json'}
        skill_query_url = f"https://square.ukp-lab.de/api/skill-manager/skill/{skill_id}/query" #note I hardcoded square URL here
        model_predictions = list()
        # i = 0
        for request in model_inputs["request"]:
            response = requests.post(skill_query_url, data=json.dumps(request), headers=headers)
            predictions = response.json()
            model_predictions.append(predictions["predictions"][0]["prediction_output"]["output"])
            # i += 1
            # if i == 10:
            #     break

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
                    "skill_id": skill_id,
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
        logging.info(ex)
    return model_outputs


