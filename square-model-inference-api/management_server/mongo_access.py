from pymongo import MongoClient
import logging

# ToDo make this environment variables
username = "root"
password = "example"

client = MongoClient('mongodb://%s:%s@%s' % (username, password, "mongo"))
logger = logging.getLogger(__name__)


async def check_identifier_new(identifier):
    db = client.model_management
    models = db.models
    if models.count_documents({"identifier": identifier}) >= 1:
        return False
    else:
        return True


async def add_model_db(identifier, env):
    data = env.copy()
    data["identifier"] = identifier
    db = client.model_management
    models = db.models

    if models.count_documents({"identifier": identifier}) >= 1:
        return False

    models.insert_one(data)
    return True


async def remove_model_db(identifier):
    query = {"identifier": identifier}
    db = client.model_management
    models = db.models
    models.delete_one(query)


async def get_models_db():
    db = client.model_management
    models = db.models
    results = []
    for m in models.find():
        logger.info("Result type: {}".format(type(m)))
        results.append(m)
    return results


async def update_model_db(identifier, updated_params):
    db = client.model_management
    models = db.models
    query = {"identifier": identifier}
    new_values = {"$set": {
        "MAX_INPUT_SIZE": updated_params.max_input,
        "DISABLE_GPU": updated_params.disable_gpu,
        "BATCH_SIZE": updated_params.batch_size,
        "RETURN_PLAINTEXT_ARRAYS": updated_params.return_plaintext_arrays,
    }}
    models.update_one(query, new_values)


async def init_db(deployed_models):
    db = client.model_management
    models = db.models
    added_models = []
    for data in deployed_models:
        if models.count_documents({"identifier": data["identifier"]}) == 0:
            models.insert_one(data)
            added_models.append(data["identifier"])
    return added_models
