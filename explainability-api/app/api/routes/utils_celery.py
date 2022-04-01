import json


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

def create_file_paths(skill_id):
    """Get the directory

    This function creates and return the directory of the json file containing the test cases

    Args:
        skill_id (str) : ID of the skill
    
    Returns:
        test_file_path (str) : Directory of the file containing the test cases
    
    """

    test_file_path = "api/routes/tests/"
    # prediction_file_path = current_dir + "/predictions/" + skill_id + ".json"
    return test_file_path

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