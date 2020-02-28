import json
from .selectors import BaseSelector

SELECTORS = {
    "base": BaseSelector
}


class SkillSelector:
    def __init__(self):
        self.selectors = {}
        self.skills = []
        self.config = None

    def init_from_json(self, config):
        with open(config) as f:
            self.config = json.load(f)["skillSelector"]
        self.selectors = {selector["name"]: SELECTORS[selector["name"]](**selector["config"])
                          for selector in self.config["selectors"]}

    def get_selectors(self):
        return list(self.selectors.keys())

    def query(self, request):
        question = request["question"]
        options = request["options"]
        selector = self.selectors[options["selector"]]
        return selector.query(question, options)