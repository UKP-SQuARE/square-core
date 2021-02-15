import time
import json
import os

import http.client

import requests
import eventlet
import logging
from itertools import repeat

from elasticsearch.helpers import bulk
from sqlalchemy import and_, func
from elasticsearch import Elasticsearch

from squareapi.models import db, SkillExampleSentence

logger = logging.getLogger(__name__)

# Global pool for all requests
pool = eventlet.GreenPool()


class TrainingException(Exception):
    pass


class UnpublishException(Exception):
    pass


class Selector:
    """
    Selector base class for all selector implementations
    """

    def query(self, question, options, generator=False):
        """
        Answers a query with the skills chosen by the selector.
        If the selector needs to be trained, then only skills with is_published==True will be considered since the selector is trained for them.
        :param question: the query question
        :param options: the options for the query
        :param generator: flag to indicate that the results should be returned once they come in from a skill via generator
        or that the result should contain all answers together once all skills have answered
        :return: the responses from the skills or a generator for the responses
        """
        raise NotImplementedError

    def train(self, id):
        """
        Train the selector for a new skill uniquely identified by the id.
        Training data is found in the database.
        A TrainingException is raised if there are any problems with the training that prevent its completion.
        :param id: Unique id of the skill. This id will be available in query() for the selected skills
        :raise TrainingException: raised if there are any problems with the training that prevent its completion
        """
        raise NotImplementedError

    def unpublish(self, id):
        """
        Remove the skill from the trained skills of this selector
        :param id: id of the skill to remove
        :raise UnpublishException: raised if there are any problems with the process that prevent its completion
        """
        raise NotImplementedError

    @staticmethod
    def request_skill(question, options, skill, score):
        """
        Send a query request to a skill.
        maxResultsPerSkill is enforced by this method.
        :param question: the question for the query
        :param options: the options for the query
        :param skill: the skill to query
        :param score: the relevance score for the skill valued [0;1]
        :return: the answer of the query with additional informations about the skill
        """
        maxResults = int(options["maxResultsPerSkill"])
        host = skill["url"].split()
        url = skill["url"].split("/")[2]
        host = url.split(":")[0]
        port = int(url.split(":")[1])

        try:
            conn = http.client.HTTPConnection(host, port)
            payload = {
               "question": question,
               "options": {
                   "maxResults": maxResults
               }
            }
            headers = {'Content-type': 'application/json'}
            conn.request("POST", "/api/query", json.dumps(payload), headers)
            resp = conn.getresponse()
            data = resp.read().decode("utf-8")
            json_obj = json.loads(data)
            return {"name": skill["name"], "score": score, "skill_description": skill["description"], "results": json_obj[:maxResults]}
        except requests.Timeout as e:
            return {"name": skill["name"], "score": score, "skill_description": skill["description"], "error": str(e)}
        except requests.ConnectionError as e:
            return {"name": skill["name"], "score": score, "skill_description": skill["description"], "error": str(e)}

    @staticmethod
    def query_skills(question, options, skills, scores):
        """
        Query all skills in a given list asynchronously.
        The result is returned once all skills have answered.
        :param question: the question for the query
        :param options: the options for the query
        :param skills: the skills to query
        :param scores: the relevance scores for the skill valued [0;1]. Scores do not need to add up to 1 and even can be larger in total
        :return: a list of all query responses
        """
        logger.debug("Chose the following skill for the question '{}': {}".format(
            question, ", ".join(["{} ({:.4f})".format(skill["name"], score) for skill, score in zip(skills, scores)])))
        results = []
        count = len(skills)
        if count == 0:
            return [{"name": "There was a problem", "score": 0,  "error": "No skills were chosen."}]
        for skill_result in pool.imap(Selector.request_skill, repeat(question, count), repeat(options, count), skills, scores):
            results.append(skill_result)
        return results

    @staticmethod
    def query_skills_generator(question, options, skills, scores):
        """
        Query all skills in a given list asynchronously.
        The result are yielded as they come in.
        :param question: the question for the query
        :param options: the options for the query
        :param skills: the skills to query
        :param scores: the relevance scores for the skill valued [0;1]. Scores do not need to add up to 1 and even can be larger in total
        :return: a generator for a list of all query responses
        """
        logger.debug("Chose the following skill for the question '{}': {}".format(
            question, ", ".join(["{} ({:.4f})".format(skill["name"], score) for skill, score in zip(skills, scores)])))
        count = len(skills)
        if count == 0:
            yield [{"name": "There was a problem", "score": 0,  "error": "No skills were chosen."}]
        for skill_result in pool.imap(Selector.request_skill, repeat(question, count), repeat(options, count), skills, scores):
            yield skill_result

    @staticmethod
    def _filter_unpublished_skills(skills):
        """
        Return a list with all skills that are not published removed
        :param skills: the skill list to filter
        :return: a list with all skills that are not published removed
        """
        return [skill for skill in skills if skill["is_published"]]


class BaseSelector(Selector):
    """
    A simple base selector that always chooses the first maxQuerriedSkills skills in the options to query.
    This selector can be used if a developer wants to query specific skills.
    """
    def __init__(self):
        super(BaseSelector, self).__init__()

    def query(self, question, options, generator=False):
        skills = options["selectedSkills"][:int(options["maxQuerriedSkills"])]
        scores = [1]*len(skills)
        if generator:
            return self.query_skills_generator(question, options, skills, scores)
        else:
            return self.query_skills(question, options, skills, scores)

    def train(self, id):
        # BaseSelector needs no training.
        pass

    def unpublish(self, id):
        # BaseSelector needs no training so there is nothing to unpublish.
        pass


class ElasticsearchVoteSelector(Selector):
    """
    This selector retrieves k training sentences similar to the question from Elasticsearch and then performs a (weighted) vote similar to kNNN
    to decide on relevant skills.
    Only uses published skills.
    """

    """
    Available weighting schemes:
    uniform: each retrieved question has equal weight
    score: each retrieved question is weighted proportional to their similarity score given by Elasticsearch
    """
    WEIGHTINGS = {"uniform", "score"}

    """
    Mapping for the ES Index that holds the training data
    """
    ES_MAPPING = {
        "mappings": {
            "properties": {
                "question_id": { # Id of the question in the DB
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

    def __init__(self, elasticsearch, k=50, weighting="uniform", weight_by_number_examples=True):
        """
        :param elasticsearch: config for Elasticsearch instance
        :param k: the number of retrieved questions from Elasticsearch; the k in kNN
        :param weighting: the weighting scheme chosen from WEIGHTINGS
        """
        super(ElasticsearchVoteSelector, self).__init__()

        self.es = Elasticsearch(hosts=[elasticsearch["url"]], index=elasticsearch["index"])
        self.es.index_name = elasticsearch["index"]
        logger.info("Waiting for Elasticsearch at {} to start...".format(elasticsearch["url"]))
        while not self.es.ping():
            logger.info("Cannot connect to Elasticsearch. Retrying in 30s.")
            time.sleep(30)
        logger.info("Waiting for Elasticsearch to be ready...")
        self.es.cluster.health(wait_for_status='yellow', request_timeout=120)
        if not self.es.indices.exists(self.es.index_name):
            logger.info("Elasticsearch Index {} does not exist. Creating it...".format(self.es.index_name))
            self.es.indices.create(index=self.es.index_name, body=self.ES_MAPPING)

        self.k = k
        if weighting in self.WEIGHTINGS:
            self.weighting = weighting
        else:
            raise ValueError("Weighting {} is not in the set of available weightings {}".format(weighting, self.WEIGHTINGS))

        self.skill_example_count = None
        self.weight_by_number_examples = weight_by_number_examples
        self._update_skill_example_count()

    def _update_skill_example_count(self):
        if self.weight_by_number_examples:
            res = db.session.query(func.count(SkillExampleSentence.skill_id), SkillExampleSentence.skill_id).group_by(SkillExampleSentence.skill_id).all()
            self.skill_example_count = {b[1]: b[0] for b in res}

    def query(self, question, options, generator=False):
        skills = self._filter_unpublished_skills(options["selectedSkills"])
        selected_skills, scores = self.scores(question, skills, int(options["maxQuerriedSkills"]))
        if generator:
            return self.query_skills_generator(question, options, selected_skills, scores)
        else:
            return self.query_skills(question, options, selected_skills, scores)

    def scores(self, question, skills, max_querried_skills):
        """
        Retrieves k training sentences similar to the question from Elasticsearch and then performs a (weighted) vote similar to kNNN
        to decide on relevant skills.

        Scores do not imply confidence that a skill is truly relevant but only that it is more relevant than other skills.
        In fact, if the vote is really unsure (e.g. three skills get 33% of the votes each), then many skills will get a high score.
        :param question: the question for which we want relavant skills
        :param skills: the subset of all published skills that the chosen skills are taken from
        :param max_querried_skills: the maximum number of skills that are chosen
        :return: an iterable of the chosen skills and an iterable of their respective scores
        """
        res = self.es.search(index=self.es.index_name, body={
            "size": self.k,
            "query": {
                "match": {"question_text": question}
            }
        })
        res = res["hits"]["hits"]
        if self.weighting == "uniform":
            weights = [1/len(res)]*len(res)
        elif self.weighting == "score":
            weights = [r["_score"] for r in res]

        # vote score for all skills, not only selected
        votes = {}
        for r, w in zip(res, weights):
            rs = r["_source"]
            if self.skill_example_count is not None:
                w = w/self.skill_example_count[rs["skill_id"]]
            if rs["skill_id"] in votes:
                votes[rs["skill_id"]] += w
            else:
                votes[rs["skill_id"]] = w
        total_weight = sum(votes.values())
        votes = {key: votes[key]/total_weight for key in votes}
        max_score = max(votes.values())
        # now we reduce to only the selected skills and we only select first maxQuerriedSkills ; if they are not in votes, they get a score of 0
        # we also [0-1]-normalize the scores
        skills_with_score = sorted([(skill, votes[skill["id"]]/max_score if skill["id"] in votes else 0.0)
                                    for skill in skills], key=lambda v: v[1], reverse=True)[:max_querried_skills]

        selected_skills, scores = zip(*skills_with_score)
        return selected_skills, scores

    def train(self, id):
        sentences = SkillExampleSentence.query.filter(and_(SkillExampleSentence.skill_id == id, SkillExampleSentence.is_dev == False)).all()
        es_sentences = ({
            "_index": self.es.index_name,
            "_source": {
                'question_id': sent.id,
                'question_text': sent.sentence,
                'skill_id': id
            }
        } for sent in sentences)
        success, info = bulk(self.es, es_sentences, request_timeout=5*60, max_retries=5)
        db.session.remove()
        self._update_skill_example_count()
        if not success:
            raise TrainingException("Failed to add training examples to Elasticsearch. Aborting training. Response from Elasticsearch was: {}".format(info))

    def unpublish(self, id):
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {"skill_id": id}
                    }
                }
            }
        }
        self.es.delete_by_query(index=[self.es.index_name], body=body, refresh=True)


class TransformerSelector(Selector):
    """
    This selector is a Transformer model with an classification head for each skill which gives a relevance score for
    each skill which is used for the ranking.
    Only uses published skills.
    """
    def __init__(self, transformer_server_url):
        """
        :param transformer_server_url: the URL to the transformer server (a running instance of the server in the folder transformer-selector-backend)
        """
        super(TransformerSelector, self).__init__()
        self.server_url = transformer_server_url
        try:
            r = requests.get("{}/api/ping".format(self.server_url)).json()
        except Exception as e:
            raise RuntimeError("Cannot connect to Transformer Server at {}".format(transformer_server_url), e)

    def query(self, question, options, generator=False):
        skills = self._filter_unpublished_skills(options["selectedSkills"])
        selected_skills, scores = self.scores(question, skills, int(options["maxQuerriedSkills"]))
        if generator:
            return self.query_skills_generator(question, options, selected_skills, scores)
        else:
            return self.query_skills(question, options, selected_skills, scores)

    def scores(self, question, skills, max_querried_skills):
        skill_id_map = {skill["id"]: skill for skill in skills}
        skillid_score_tuples = requests.get("{}/api/scores".format(self.server_url), params={"question": question}).json()
        skills_with_score = sorted([(skill_id_map[skillid], score) for (skillid, score) in skillid_score_tuples],
                                   key=lambda v: v[1], reverse=True)[:max_querried_skills]

        selected_skills, scores = zip(*skills_with_score)
        return selected_skills, scores

    def train(self, id):
        training_result = requests.post("{}/api/train".format(self.server_url), params={"id": id}).json()
        if not training_result["success"]:
            raise TrainingException("Exception during training: {}".format(training_result["msg"]))

    def unpublish(self, id):
        unpublish_result = requests.post("{}/api/unpublish".format(self.server_url), params={"id": id}).json()
        if not unpublish_result["success"]:
            raise UnpublishException("Exception during training: {}".format(unpublish_result["msg"]))