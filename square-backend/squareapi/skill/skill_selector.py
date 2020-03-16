from collections import OrderedDict
from .selectors import TrainingException, UnpublishException, BaseSelector
import logging
import eventlet
from elasticsearch import Elasticsearch
from itertools import repeat
from ..models import Skill, db

logger = logging.getLogger(__name__)

# Global pool for all requests
pool = eventlet.GreenPool()

"""
All implemented selectors and their names
"""
SELECTORS = {
    "base": BaseSelector
}


def train_selector(selector_name, selector, skill, sentences):
    """
    Train a given selector for a new skill with training sentences.
    :param selector_name: name of the selector (for logging)
    :param selector: the selector object
    :param skill: the skill obeject with unique id
    :param sentences: the training sentences
    :return: Boolean indicating the success and a JSON-ready response
    """
    try:
        selector.train(skill["id"], sentences)
        succ_msg = "Trained selector {} for skill {}".format(selector_name, skill["id"])
        logger.info(succ_msg)
        return True, {"msg": succ_msg}
    except TrainingException as e:
        error_msg = "Failed to train selector {} for skill {}: {}".format(selector_name, skill["id"], e)
        logger.critical(error_msg)
        return False, {"error", error_msg}


def unpublish_selector(selector_name, selector, skill):
    """
    Unpublish a skill for a given selector.
    :param selector_name: name of the selector (for logging)
    :param selector: the selector object
    :param skill: the skill obeject with unique id
    :return: Boolean indicating the success and a JSON-ready response
    """
    try:
        selector.unpublish(skill["id"])
        succ_msg = "Unpublished selector {} for skill {}".format(selector_name, skill["id"])
        logger.info(succ_msg)
        return True, {"msg": succ_msg}
    except UnpublishException as e:
        error_msg = "Failed to unpublish selector {} for skill {}: {}".format(selector_name, skill["id"], e)
        logger.critical(error_msg)
        return False, {"error", error_msg}


class SkillSelector:
    """
    Bridge between the API and the selector implementations.
    """
    def __init__(self):
        self.selectors = {}
        self.skills = []
        self.config = None
        self.es = None

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

    def train(self, skill, sentences, generator=False):
        """

        :param skill:
        :param sentences:
        :param generator: if true, returns a generator that yields status messages of the training
        :return: if generator is true, returns a generator that yields status messages of the training, otherwise nothing is returned
        """
        if generator:
            return self._train_generator(skill, sentences)

        results = []
        # TODO add to ES
        count = len(self.selectors)
        for result, msg in pool.starmap(train_selector, [(selector, self.selectors[selector], s, sent)
                                                         for selector, s, sent in
                                                         zip(self.selectors, repeat(skill, count), repeat(sentences, count))]):
            results.append(result)
        if all(results):
            db_skill = Skill.query.filter_by(id=skill["id"]).first()
            db_skill.set_publish(True)
            db.session.commit()
            msg = "Successfully trained all selectors with skill {}. Skill is now published".format(skill["name"])
            logger.info(msg)
        else:
            self.unpublish(skill, generator=False)
            msg = "Failed to train all selectors with skill {}. Rolled training back".format(skill["name"])
            logger.info(msg)

    def _train_generator(self, skill, sentences):
        """
        Generator variation of train()
        :return: yields status messages of the training
        """
        results = []
        # TODO add to ES
        count = len(self.selectors)
        for result, msg in pool.starmap(train_selector, [(selector, self.selectors[selector], s, sent)
                                                         for selector, s, sent in
                                                         zip(self.selectors, repeat(skill, count), repeat(sentences, count))]):
            results.append(result)
            yield msg
        if all(results):
            db_skill = Skill.query.filter_by(id=skill["id"]).first()
            db_skill.set_publish(True)
            db.session.commit()
            msg = "Successfully trained all selectors with skill {}. Skill is now published".format(skill["name"])
            logger.info(msg)
            yield {"msg": msg}
        else:
            self.unpublish(skill, generator=False)
            msg = "Failed to train all selectors with skill {}. Rolled training back".format(skill["name"])
            logger.info(msg)
            yield {"error", msg}

    def unpublish(self, skill, generator=False):
        """

        :param skill:
        :param generator: if true, returns a generator that yields status messages of the process
        :return: if generator is true, returns a generator that yields status messages of the process, otherwise nothing is returned
        """
        if generator:
            return self._unpublish_generator(skill)

        count = len(self.selectors)
        for result, msg in pool.starmap(unpublish_selector, [(selector, self.selectors[selector], s)
                                                             for selector, s in zip(self.selectors, repeat(skill, count))]):
            pass
        db_skill = Skill.query.filter_by(id=skill["id"]).first()
        db_skill.set_publish(False)
        db.session.commit()
        db.session.remove()
        # TODO remove from ES
        msg = "Skill {} is now unpublished".format(skill["name"])
        logger.info(msg)

    def _unpublish_generator(self, skill):
        """
        Generator variation of unpublish()
        :return: yields status messages of the process
        """
        count = len(self.selectors)
        for result, msg in pool.starmap(unpublish_selector, [(selector, self.selectors[selector], s)
                                                             for selector, s in zip(self.selectors, repeat(skill, count))]):
            yield msg
        db_skill = Skill.query.filter_by(id=skill["id"]).first()
        db_skill.set_publish(False)
        db.session.commit()
        db.session.remove()
        # TODO remove from ES
        msg = "Skill {} is now unpublished".format(skill["name"])
        logger.info(msg)
        yield {"msg": msg}