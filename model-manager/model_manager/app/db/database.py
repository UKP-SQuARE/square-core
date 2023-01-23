import logging

from pymongo import MongoClient

from model_manager.app.core.mongo_config import MongoSettings
from model_manager.app.routers import utils


logger = logging.getLogger(__name__)


class MongoClass:
    """
    class to handle the initialization and operation of mongodb
    """
    def __init__(self):
        """
        get mongo settings and initialize db
        """
        mongo_settings = MongoSettings()
        # logger.info(mongo_settings.connection_url)  # private
        self.client = MongoClient(mongo_settings.connection_url)
        self.db = self.client.model_management  # database
        self.models = self.db.models  # collection
        self.containers = self.db.containers  # collection

    def close(self):
        """
        close mongo db connection
        """
        self.client.close()

    async def check_identifier_new(self, identifier) -> bool:
        """
        check if model identifier is in db
        """
        if self.models.count_documents({"IDENTIFIER": identifier}) >= 1:
            return False
        return True

    async def check_user_id(self, request, identifier) -> bool:
        """
        check user id requesting a resource
        """
        models = await self.get_models_db()
        model_config = [m for m in models if m["IDENTIFIER"] == identifier][0]
        check_user = bool(model_config["USER_ID"] == await utils.get_user_id(request))
        return check_user

    def server_info(self):
        return self.client.server_info()

    async def add_model_db(self, env, allow_overwrite=False):
        """
        add entry to the db
        """
        data = env.copy()
        identifier = data["IDENTIFIER"]
        container = env["CONTAINER"]
        del env["CONTAINER"]
        if self.models.count_documents({"IDENTIFIER": identifier}) >= 1:
            if allow_overwrite:
                query = {"IDENTIFIER": identifier}
                self.models.delete_one(query)
            else:
                return False

        self.models.insert_one(data)

        return await self.add_container(env["IDENTIFIER"], container)

    async def add_container(self, identifier, container):
        container_data = {
            "IDENTIFIER": identifier,
            "CONTAINER": container
        }
        self.containers.insert_one(container_data)
        return True

    async def remove_container(self, containers):
        for c in containers:
            query = {"CONTAINER": c}
            self.containers.delete_one(query)
        return True

    def get_model_container_ids(self, identifier):
        query = {"IDENTIFIER": identifier}
        result = self.containers.find(query)
        return result

    async def get_model_containers(self):
        pipeline = [
            {"$group": {"_id": "$IDENTIFIER", "count": {"$sum": 1}}},
        ]
        logger.info(self.containers.aggregate(pipeline))
        return self.containers.aggregate(pipeline)

    def get_container_id(self, identifier):
        """
        get container id from db
        """
        query = {"IDENTIFIER": identifier}
        result = self.containers.find_one(query)
        logger.info(result)
        return result["CONTAINER"]

    async def remove_model_db(self, identifier):
        """
        remove entry from db
        """
        query = {"IDENTIFIER": identifier}
        self.models.delete_one(query)
        self.containers.delete_many(query)

    async def get_models_db(self):
        """
        get db entries
        """
        results = []
        for model in self.models.find():
            logger.info("Result type: %s", type(model))
            results.append(model)
        return results

    async def update_model_db(self, identifier, updated_params):
        """
        Update db entries
        """
        query = {"IDENTIFIER": identifier}
        new_values = {
            "$set": {
                "MAX_INPUT_SIZE": updated_params.max_input,
                "DISABLE_GPU": updated_params.disable_gpu,
                "BATCH_SIZE": updated_params.batch_size,
                "RETURN_PLAINTEXT_ARRAYS": updated_params.return_plaintext_arrays,
            }
        }
        self.models.update_one(query, new_values)

    async def init_db(self, deployed_models):
        """
        add deployed models to db
        """
        added_models = []
        for data in deployed_models:
            if self.models.count_documents({"IDENTIFIER": data["IDENTIFIER"]}) == 0:
                await self.add_model_db(data)
                added_models.append(data["IDENTIFIER"])
        return added_models

    async def get_model_stats(self, identifier):
        query = {"IDENTIFIER": identifier}
        return self.models.find_one(query)

    async def get_containers(self, identifier, num):
        query = {"IDENTIFIER": identifier}
        result = self.containers.find(query, sort=[('_id', -1)]).limit(num)
        containers = []
        for c in result:
            containers.append(c["CONTAINER"])
        return containers
