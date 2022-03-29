from pymongo import MongoClient
from app.core.mongo_config import MongoSettings
from app.routers import utils

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

    async def check_identifier_new(self, identifier)-> bool:
        if self.models.count_documents({"identifier": identifier}) >= 1:
            return False
        else:
            return True

    async def check_user_id(self, request, identifier) -> bool:
        models = await self.get_models_db()
        model_config = [m for m in models if m["identifier"] == identifier][0]
        check_user = True if model_config["user_id"] == await utils.get_user_id(request) else False
        return check_user

    def server_info(self):
        return self.client.server_info()

    async def add_model_db(self, user_id, identifier, env, allow_overwrite=False):
        """
        add entry to the db
        """
        data = env.copy()
        data["identifier"] = identifier
        data["user_id"] = user_id

        if self.models.count_documents({"identifier": identifier}) >= 1:
            if allow_overwrite:
                query = {"identifier": identifier}
                self.models.delete_one(query)
            else:
                return False

        self.models.insert_one(data)
        return True

    def get_container_id(self, identifier):
        query = {"identifier": identifier}
        result = self.models.find_one(query)
        logger.info(result)
        return result["container"]

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
