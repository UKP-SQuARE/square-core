import pymongo

from skill_manager.settings.mongo_settings import MongoSettings

class MongoClient():

    def connect(self):
        mongo_settings = MongoSettings()
        self.client = pymongo.MongoClient(mongo_settings.connection_url)

    def close(self):
        self.client.close()
