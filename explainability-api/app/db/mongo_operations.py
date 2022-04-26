import logging

from pymongo import MongoClient

from app.core.mongo_config import MongoSettings


logger = logging.getLogger(__name__)


class Database:
    """
    class to handle the initialization and operation of mongodb
    """
    def __init__(self):
        """
        get mongo settings and initialize db
        """
        mongo_settings = MongoSettings()
        self.client = MongoClient(mongo_settings.connection_url)
        self.db = self.client.checklist_data  # database
        self.checklist_tests = self.db.checklist_tests  # collection
        self.checklist_results = self.db.checklist_results  # collection

    def close(self):
        """
        close mongo db connection
        """
        self.client.close()

    # async def check_identifier_new(self, identifier) -> bool:
    #     """
    #     check if model identifier is in db
    #     """
    #     if self.models.count_documents({"IDENTIFIER": identifier}) >= 1:
    #         return False
    #     return True
    #
    # async def check_user_id(self, request, identifier) -> bool:
    #     """
    #     check user id requesting a resource
    #     """
    #     models = await self.get_models_db()
    #     model_config = [m for m in models if m["IDENTIFIER"] == identifier][0]
    #     check_user = bool(model_config["USER_ID"] == await utils.get_user_id(request))
    #     return check_user

    def server_info(self):
        return self.client.server_info()

    async def add_tests_to_db(self, env):
        """
        add entry to the db
        """
        try:
            data = env.copy()
            if self.checklist_tests.count_documents({"qa_type": data["qa_type"],
                                                     "test_name": data["test_name"]}) >= 1:
                # print("Entry already present in db. Skipping!")
                logger.info("Entry already present in db. Skipping!")
                return False
            else:
                self.checklist_tests.insert_one(data)
                return True
        except ValueError:
            return False

    def get_tests_from_db(self, qa_type):
        """
        get container id from db
        """
        result = list()
        if self.checklist_tests.count_documents({"qa_type": qa_type}) >= 1:
            query = {"qa_type": qa_type}
            docs = self.checklist_tests.find(query)
            result = [test for test in docs]
            logger.info(result)
        else:
            logger.info("No tests to run for the specified qa_type")
            return result
        return result
