import logging
from typing import List

from pymongo import MongoClient

from app.core.mongo_config import MongoSettings
from app.models.checklist import ChecklistTests, ChecklistResults


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
        self.db = self.client.explainability  # database
        # await initiate_database()
        self.checklist_tests = self.db.checklist_tests   # collection
        self.checklist_results = self.db.checklist_results  # collection

    def close(self):
        """
        close mongo db connection
        """
        self.client.close()

    def server_info(self):
        return self.client.server_info()

    async def add_tests_to_db(self, env: ChecklistTests) -> bool:
        """
        add entry to the db
        """
        try:
            data = env.copy()
            if self.checklist_tests.count_documents(
                    {
                        "qa_type": data["qa_type"],
                        "test_name": data["test_name"]
                    }
            ) >= 1:
                # print("Entry already present in db. Skipping!")
                logger.info("Entry already present in db. Skipping!")
                return False
            else:
                self.checklist_tests.insert_one(data)
                return True
        except ValueError:
            return False

    def get_tests_from_db(self, qa_type: str) -> list:
        """
        get container id from db
        """
        result = list()
        if self.checklist_tests.count_documents({"qa_type": qa_type}) >= 1:
            query = {"qa_type": qa_type}
            docs = self.checklist_tests.find(query)
            result = [test for test in docs]
            # logger.info(result)
        else:
            logger.info("No tests to run for the specified qa_type")
            return result
        return result

    async def add_results_to_db(self, model_outputs: List[ChecklistResults]) -> bool:
        """
        add checklist results to the db
        """
        try:
            for predictions in model_outputs:
                data = predictions.copy()
                if self.checklist_results.count_documents(
                        {
                            "skill_id": data["skill_id"],
                            "question": data["question"]
                        }
                ) >= 1:
                    # print("Entry already present in db. Skipping!")
                    logger.info("Entry already present in db. Skipping!")
                    return False
                else:
                    self.checklist_results.insert_one(data)
            return True
        except ValueError:
            return False

    async def add_to_db(self, collection, data, query) -> bool:
        try:
            if self.checklist_results.count_documents(query) >= 1:
                logger.info("Entry already present in db. Skipping!")
                return False
            else:
                self.checklist_results.insert_one(data)
        except ValueError:
            return False
