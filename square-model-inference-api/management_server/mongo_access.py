from pymongo import MongoClient
from app.core.mongo_config import MongoSettings

import logging
logger = logging.getLogger(__name__)


class MongoClass:
    def __init__(self):
        """
        get mongo settings and initialize db
        """
        mongo_settings = MongoSettings()
        self.client = MongoClient(mongo_settings.connection_url)
        self.db = self.client.model_management  # database
        self.models = self.db.models            # collection

    def close(self):
        """
        close mongo db connection
        """
        self.client.close()

    async def add_model_db(self, identifier, env):
        """
        add entry to the db
        """
        data = env.copy()
        data["identifier"] = identifier

        if self.models.count_documents({"identifier": identifier}) >= 1:
            return False

        self.models.insert_one(data)
        return True

    async def remove_model_db(self, identifier):
        """
        remove entry from db
        """
        query = {"identifier": identifier}
        self.models.delete_one(query)

    async def get_models_db(self):
        """
        get db entries
        """
        results = []
        for m in self.models.find():
            logger.info("Result type: {}".format(type(m)))
            results.append(m)
        return results

    async def update_model_db(self, identifier, updated_params):
        """
        Update db entries
        """
        query = {"identifier": identifier}
        new_values = {"$set": {
            "MAX_INPUT_SIZE": updated_params.max_input,
            "DISABLE_GPU": updated_params.disable_gpu,
            "BATCH_SIZE": updated_params.batch_size,
            "RETURN_PLAINTEXT_ARRAYS": updated_params.return_plaintext_arrays,
        }}
        self.models.update_one(query, new_values)

    async def init_db(self, deployed_models):
        """
        add deployed models to db
        """
        added_models = []
        for data in deployed_models:
            if self.models.count_documents({"identifier": data["identifier"]}) == 0:
                self.models.insert_one(data)
                added_models.append(data["identifier"])
        return added_models
