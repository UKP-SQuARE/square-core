from collections import OrderedDict
from .selectors import BaseSelector
import logging

logger = logging.getLogger(__name__)

"""
All implemented selectors and their names
"""
SELECTORS = {
    "base": BaseSelector
}


class SkillSelector:
    """
    Interface between the API and the selector implementations. The API can decide which selector should be used for a request.
    """
    def __init__(self):
        self.selectors = {}
        self.skills = []
        self.config = None

    def init_from_config(self, config):
        """
        Initialize all requested selectors given in the config
        :param config: dict containing a list of selectors in the given format: skillSelector: [{name, config}]
        """
        self.config = config["skillSelector"]
        self.selectors = OrderedDict([(selector["name"], SELECTORS[selector["name"]](**selector["config"]))
                          for selector in self.config["selectors"]])
        logger.debug("Initialized these selectors: {}".format(", ".join(self.selectors.keys())))

    def get_selectors(self):
        """
        Get a list of the names of all initilized selectors
        :return: a list of the names of all initilized selectors
        """
        return list(self.selectors.keys())

    def query(self, request, generator=False):
        """
        Send the request to the selector chosen in the request.
        :param request: a request for a selector with a selector name set in the options
        :param generator: flag to indicate that the results should be returned once they come in from a skill via generator
        or that the result should contain all answers together once all skills have answered
        :return: the response from the selector
        """
        question = request["question"]
        options = request["options"]
        selector = self.selectors[options["selector"]]
        logger.debug("Query with selector {}".format(options["selector"]))
        return selector.query(question, options, generator)
