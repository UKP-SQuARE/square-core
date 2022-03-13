from pymongo import MongoClient
import logging

username = "root"
password = "example"

client = MongoClient('mongodb://%s:%s@%s' % (username, password, "mongo"))
logger = logging.getLogger(__name__)


async def add_model_db(identifier, env):
    data = env.copy()
    data["identifier"] = identifier
    db = client.model_management
    models = db.models

    if models.count_documents({"identifier": identifier}) >= 1:
        return False

    models.insert_one(data)
    return True


async def remove_model_dm(identifier):
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