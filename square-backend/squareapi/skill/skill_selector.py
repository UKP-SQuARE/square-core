import time
from collections import OrderedDict
from .selectors import TrainingException, UnpublishException, BaseSelector, ElasticsearchVoteSelector
import logging
import eventlet
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from itertools import repeat
from ..models import Skill, db

logger = logging.getLogger(__name__)

# Global pool for all requests
pool = eventlet.GreenPool()

"""
All implemented selectors and their names
"""
SELECTORS = {
    "Base": {
        "class": BaseSelector,
        "description": "Selects the first n skills. Works with unpublished skills, too."
    },
    "Elasticsearch": {
        "class": ElasticsearchVoteSelector,
        "description": "Select based on vote between similar questions retrieved with Elasticsearch. Published skills only."
    }
}

"""
Mapping for the ES Index that holds the training data
"""
ES_MAPPING = {
    "mappings": {
        "properties": {
            "question_idx": { # Number of the question within the questions of a skill
                "type": "integer"
            },
            "question_text": { # The Question
                "type": "text",
            },
            "skill_id": { # Unique skill id
                "type": "keyword",
            }
        }
    }
}


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
        Initialize all requested selectors given in the config and initializes the Elasticsearch server
        :param config: dict containing the config with a list of selectors in the given format: skillSelector: [{name, config}]
        and with the config for the ELasticsearch server
        """
        self.config = config

        self.es = Elasticsearch(hosts=[config["elasticsearch"]["url"]], index=config["elasticsearch"]["index"])
        self.es.index_name = config["elasticsearch"]["index"]
        logger.info("Waiting for Elasticsearch at {} to start...".format(config["elasticsearch"]["url"]))
        while not self.es.ping():
            logger.info("Cannot connect to Elasticsearch. Retrying in 1 minute.")
            time.sleep(60)
        logger.info("Waiting for Elasticsearch to be ready...")
        self.es.cluster.health(wait_for_status='yellow', request_timeout=120)
        if not self.es.indices.exists(self.es.index_name):
            logger.info("Elasticsearch Index {} does not exist. Creating it...".format(self.es.index_name))
            self.es.indices.create(index=self.es.index_name, body=ES_MAPPING)

        logger.info("Elasticsearch is ready. Now creating selectors")

        # OrderedDict so that we preserve the order given in the config
        self.selectors = OrderedDict([(selector["name"], SELECTORS[selector["name"]]["class"](elasticsearch=self.es, **selector["config"]))
                                      for selector in self.config["skillSelector"]["selectors"]])
        logger.debug("Initialized these selectors: {}".format(", ".join(self.selectors.keys())))

    def get_selectors(self):
        """
        Get a list of the names of all initilized selectors with a description of them
        :return: a list of the names of all initilized selectors with a description of them
        """
        return [{"name": key, "description": SELECTORS[key]["description"]} for key in self.selectors.keys()]

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
        Stores the sentences in Elasticsearch and then trains all selectors for the new skill.
        Trained skills will be unpublished before they are retrained.
        :param skill: the skill to train for
        :param sentences: the training example questions
        :param generator: if true, returns a generator that yields status messages of the training
        :return: if generator is true, returns a generator that yields status messages of the training, otherwise nothing is returned
        """
        logger.info("Starting training of selectors for skill {}".format(skill["name"]))
        if generator:
            return self._train_generator(skill, sentences)

        if skill["is_published"]:
            logger.info("Skill is already published. Need to unpublish before we can train.")
            self.unpublish(skill, generator=False)

        success, info = pool.spawn(self.add_to_es, skill, sentences).wait()

        if not success:
            logger.warning("Failed to add training examples to Elasticsearch. Aborting training. Resposne from Elasticsearch was: {}".format(info))
        else:
            results = []
            count = len(self.selectors)
            for result, msg in pool.starmap(self.train_selector, [(selector, self.selectors[selector], s)
                                                                  for selector, s in zip(self.selectors, repeat(skill, count))]):
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

        if skill["is_published"]:
            logger.info("Skill is already published. Need to unpublish before we can train.")
            yield {"msg": "Skill is already published. It will be unpublished now and then trained with the new data."}
            yield from self.unpublish(skill, generator=True)

        success, info = pool.spawn(self.add_to_es, skill, sentences).wait()

        if not success:
            logger.warning("Failed to add training examples to Elasticsearch. Aborting training. Response from Elasticsearch was: {}".format(info))
            yield {"error": "Failed to store training examples. Training aborted. Please try again later."}
        else:
            count = len(self.selectors)
            for result, msg in pool.starmap(self.train_selector, [(selector, self.selectors[selector], s)
                                                             for selector, s in zip(self.selectors, repeat(skill, count))]):
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
        Unpublish a skill. This removes it from all selectors and deletes all training sentences in Elasticsearch.
        :param skill: the skill to unpublish
        :param generator: if true, returns a generator that yields status messages of the process
        :return: if generator is true, returns a generator that yields status messages of the process, otherwise nothing is returned
        """
        logger.info("Starting unpublishing of skill {}".format(skill["name"]))
        if generator:
            return self._unpublish_generator(skill)

        if not skill["is_published"]:
            logger.info("Skill is already unpublished.")
        else:
            count = len(self.selectors)
            for result, msg in pool.starmap(self.unpublish_selector, [(selector, self.selectors[selector], s)
                                                                 for selector, s in zip(self.selectors, repeat(skill, count))]):
                pass
            db_skill = Skill.query.filter_by(id=skill["id"]).first()
            db_skill.set_publish(False)
            db.session.commit()
            db.session.remove()
            res = pool.spawn(self.remove_from_es, skill).wait()
            msg = "Skill {} is now unpublished".format(skill["name"])
            logger.info(msg)

    def _unpublish_generator(self, skill):
        """
        Generator variation of unpublish()
        :return: yields status messages of the process
        """
        if not skill["is_published"]:
            logger.info("Skill is already unpublished.")
            yield {"msg": "Skill is already unpublished."}
        else:
            count = len(self.selectors)
            for result, msg in pool.starmap(self.unpublish_selector, [(selector, self.selectors[selector], s)
                                                                 for selector, s in zip(self.selectors, repeat(skill, count))]):
                yield msg
            db_skill = Skill.query.filter_by(id=skill["id"]).first()
            db_skill.set_publish(False)
            db.session.commit()
            db.session.remove()
            res = pool.spawn(self.remove_from_es, skill).wait()
            if res["failures"]:
                logger.warning("Failed to delete training data for skill {} from Elasticsearch: {}".format(skill["name"], res))
            msg = "Skill {} is now unpublished".format(skill["name"])
            logger.info(msg)
            yield {"msg": msg}

    @staticmethod
    def train_selector(selector_name, selector, skill):
        """
        Train a given selector for a new skill with training sentences.
        :param selector_name: name of the selector (for logging)
        :param selector: the selector object
        :param skill: the skill obeject with unique id
        :return: Boolean indicating the success and a JSON-ready response
        """
        try:
            selector.train(skill["id"])
            succ_msg = "Trained selector {} for skill {}".format(selector_name, skill["name"])
            logger.info(succ_msg)
            return True, {"msg": succ_msg}
        except TrainingException as e:
            error_msg = "Failed to train selector {} for skill {}: {}".format(selector_name, skill["name"], e)
            logger.warning(error_msg)
            return False, {"error", error_msg}

    @staticmethod
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
            succ_msg = "Unpublished selector {} for skill {}".format(selector_name, skill["name"])
            logger.info(succ_msg)
            return True, {"msg": succ_msg}
        except UnpublishException as e:
            error_msg = "Failed to unpublish selector {} for skill {}: {}".format(selector_name, skill["name"], e)
            logger.warning(error_msg)
            return False, {"error", error_msg}

    def add_to_es(self, skill, sentences):
        """
        Add the sentences to Elasticsearch under the given skill
        :param skill: the skill to which the sentences belong
        :param sentences: the training sentences
        :return: result of the indexing
        """
        es_sentences = ({
            "_index": self.es.index_name,
            "_source": {
                'question_idx': i,
                'question_text': sent.strip(),
                'skill_id': skill["id"]
            }
        } for i, sent in enumerate(sentences))
        success, info = bulk(self.es, es_sentences, request_timeout=5*60, max_retries=5)
        return success, info

    def remove_from_es(self, skill):
        """
        Delete the sentences to Elasticsearch under the given skill
        :param skill: the skill to which the sentences belong
        return: result of the deletion
        """
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {"skill_id": skill["id"]}
                    }
                }
            }
        }
        return self.es.delete_by_query(index=[self.es.index_name], body=body, refresh=True)