import requests
import argparse
import os
import json


def test_single_skill(request_path, skill, args):
    """ Run the tests for a single skill

    Run tests for single skill and save the results in json file

    Args:
        request_path (str) : Request path for testing the skill
        skill (dict) : A dictionary containing all the information of the skill
        args (ArgumentParser object): An object containing necessary arguments to run this script
    """
    print("testing skill")
    headers = {'Content-type': 'application/json'}
    response = requests.post(request_path, data = skill)
    json_data = response.json()
    path = os.getcwd() + "/" + args.skill_id + '.json'
    save_json(json_data, path)
    print("testing done predictions are saved in " + str(path))


def save_json(json_data, path : str):
    """ Save a json object

    Saves a json object to a specific directory

    Args:
        json_data (json_object) : Containing all the test cases and their predictions
        path (str) : Full path of the diretory where the json object will be saved

    """
    with open(path, 'w') as f:
        json.dump(json_data, f, indent=4)


def test_all_skills(request_path, skills, args):
    """ Run tests for all skills

    Run tests for all skill and save the results in different json file

    Args:
        skills (json object) : A json object containing all the information for all the objects 
        args (ArgumentParser object): An object containing necessary arguments to run this script

    """
    for skill in skills:
        if skill['skill_type'] in ['multiple-choice', 'span-extraction', 'categorical'] and "open" not in skill['name'].lower():
            print("testing " + str(skill['name']))
            skill_obj = {
                "skill_query_path" : args.skill_path + skill['id'] + "/query",
                "skill_type" : skill['skill_type'],
                "skill_base_model" : skill['default_skill_args']['base_model'],
                "skill_adapter" :skill['default_skill_args']['adapter'],
                "skill_id" : skill['id'],
                "skill_name" : skill['name']
            }
            json_skill = json.dumps(skill_obj)
            response = requests.post(request_path, data = json_skill)
            json_data = response.json()
            path = os.getcwd() + "/" + skill['id'] + '.json'
            save_json(json_data, path)
            print("testing done for " + str(skill['name']) + "and predictions are saved in " + str(path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the Explainability API')

    parser.add_argument('--all', type = bool, default = False, help = 'if True is given all skills are tested, else only the given skill is tested')
    parser.add_argument('--skill_name', type = str, default = 'BoolQ', help = 'name of the skill, change it according to need')
    parser.add_argument('--skill_type', type = str, default = 'multiple-choice', help = 'type of the skill, change it according to need')
    parser.add_argument('--skill_id', type = str, default = '61a9f66935adbbf1f2433077', help = 'id of the skill, change it according to need')
    parser.add_argument('--skill_path', type = str, 
                        default = 'https://square.ukp-lab.de/api/skill-manager/skill/', 
                        help = 'skill query path, change it according to need')
    parser.add_argument('--skill_base_model', type = str, 
                        default = 'bert-base-uncased',
                        help = 'name of the model, change it according to need')
    parser.add_argument('--skill_adapter', type = str, 
                        default = 'AdapterHub/bert-base-uncased-pf-boolq', 
                        help = 'name of the adapter, change it according to need')
    args = parser.parse_args()

    # get all the skill information
    response = requests.get("https://square.ukp-lab.de/api/skill-manager/skill")
    skills = response.json()

    # request path for testing skills
    skill_test_path = "http://localhost:8010/test"

    if args.all == True:
        test_all_skills(skill_test_path, skills, args)
    else:
        skill_obj = {
            "skill_query_path" : args.skill_path + args.skill_id + "/query",
            "skill_type" : args.skill_type,
            "skill_base_model" : args.skill_base_model,
            "skill_adapter" : args.skill_adapter,
            "skill_id" : args.skill_id,
            "skill_name" : args.skill_name,
        }
        json_skill = json.dumps(skill_obj)
        test_single_skill(skill_test_path, json_skill, args)

    # sample input to the api

    # for boolq
    # {
    #    "skill_query_path": "https://square.ukp-lab.de/api/skill-manager/skill/61a9f66935adbbf1f2433077/query",
    #    "skill_type": "categorical",
    #    "skill_base_model": "bert-base-uncased",
    #    "skill_adapter": "AdapterHub/bert-base-uncased-pf-boolq",
    #    "skill_id": "61a9f66935adbbf1f2433077"
    # }

    # for multiple choice
    # {
    #    "skill_query_path": "https://square.ukp-lab.de/api/skill-manager/skill/61a9f68535adbbf1f2433078/query",
    #    "skill_type": "multiple-choice",
    #    "skill_base_model": "bert-base-uncased",
    #    "skill_adapter": "AdapterHub/bert-base-uncased-pf-cosmos_qa",
    #    "skill_id": "61a9f68535adbbf1f2433078"
    # }

    # for span extraction
    # {
    #    "skill_query_path": "https://square.ukp-lab.de/api/skill-manager/skill/61a9f56c35adbbf1f2433072/query",
    #    "skill_type": "span-extraction",
    #    "skill_base_model": "bert-base-uncased",
    #    "skill_adapter": "AdapterHub/bert-base-uncased-pf-squad",
    #    "skill_id": "61a9f56c35adbbf1f2433072"
    # }
