import logging

import requests
import json
from fastapi import APIRouter

import checklist

router = APIRouter()


@router.get('/')
def read_root():
    return {"Hello": "World"}


@router.get('/checklist/{skill_id}', name="run checklist")
def run_checklist(skill_id: str, checklist_name: str, n_tests: int = None, test_analysis: str = None) -> list:
    """

    :param skill_id: skill id
    :param checklist_name: name of checklist
    :param n_tests: show how many test from the first onwards
    :param test_analysis: how to return the result of CheckList
    :return: output
    """
    # tested with this skill_id: 63cdbd06a8b0d566ef20cb54 - although performance is poor
    assert checklist_name is not None

    checklist_path_dict = {
        'extractive': '../checklists/extractive_model_tests.json',
        'boolean': '../checklists/boolean_model_tests.json',
        'abstractive': '../checklists/abstractive_models_tests.json',
        'multiple_choice': '../checklists/multiple_choice_model_tests.json',
        'open_domain': '../checklists/open_domain_models_tests.json',
        'open_domain_bioasq': '../checklists/open_domain_models_bioasq_tests.json'
    }

    checklist_path = checklist_path_dict[checklist_name]
    with open(checklist_path) as f:
        checklist_tests = json.load(f)

    try:
        skill_response = requests.get(f'https://square.ukp-lab.de/api/skill-manager/skill/{skill_id}')
        skill = skill_response.json()
        skill_id = skill["id"]
        # skill_type = skill["skill_type"]

        test_cases = checklist_tests['tests']
        model_inputs = checklist.create_query(skill, test_cases)

        if n_tests is not None:
            model_inputs['request'] = model_inputs["request"][:n_tests]  # if all would be too much
        else:
            model_inputs['request'] = model_inputs["request"]  # if all would be too much
        model_outputs = checklist.predict(model_inputs, skill_id)

        if test_analysis is None:
            output_return = model_outputs
        # Analysis result
        else:
            if test_analysis == 'test_type':
                output_return = checklist.test_type_analysis(model_outputs)
            elif test_analysis == 'capability':
                output_return = checklist.capability_analysis(model_outputs)
            elif test_analysis == 'test_name':
                output_return = checklist.test_name_analysis(model_outputs)

        # assert output_return is not list

        # saves output as json
        with open('temp_result/temp_result.json', 'w') as f:
            json.dump(output_return, f, indent=4)

        return output_return

    except Exception as e:
        print(e)
