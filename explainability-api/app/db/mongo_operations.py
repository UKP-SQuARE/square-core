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

    async def add_results_to_db(self, skill_id, model_outputs):
        """
        add checklist results to the db
        """
        try:
            for predictions in model_outputs:
                data = predictions.copy()
                data["skill_id"] = skill_id
                if self.checklist_results.count_documents({"skill_id": data["skill_id"],
                                                           "question": data["question"]}) >= 1:
                    # print("Entry already present in db. Skipping!")
                    logger.info("Entry already present in db. Skipping!")
                    return False
                else:
                    self.checklist_results.insert_one(data)
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
