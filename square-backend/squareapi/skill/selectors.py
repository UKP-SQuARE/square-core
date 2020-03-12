import requests
import eventlet
#import concurrent.futures as cf
import logging
from itertools import repeat

logger = logging.getLogger(__name__)

# Global pool for all requests
pool = eventlet.GreenPool()


class TrainingException(Exception):
    pass


class UnpublishException(Exception):
    pass


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
    try:
        r = requests.post("{}/query".format(skill["url"]), json={
            "question": question,
            "options": {
                "maxResults": maxResults
            }
        })
        return {"name": skill["name"], "score": score, "skill_description": skill["description"], "results": r.json()[:maxResults]}
    except requests.Timeout as e:
        return {"name": skill["name"], "score": score, "skill_description": skill["description"], "error": str(e)}
    except requests.ConnectionError as e:
        return {"name": skill["name"], "score": score, "skill_description": skill["description"], "error": str(e)}


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

    def train(self, id, sentences):
        """
        Train the selector with the given sentences for a new skill uniquely identified by the id.
        A TrainingException is raised if there are any problems with the training that prevent its completion.
        Training results such as weights should be mapped to the given id so they can later be used to score the skill for a given question.
        :param id: Unique id of the skill. This id will be available in query() for the selected skills
        :param sentences:
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
    def query_skills(question, options, skills, scores):
        """
        Query all skills in a given list asynchronously.
        The result is returned once all skills have answered.
        :param question: the question for the query
        :param options: the options for the query
        :param skills: the skills to query
        :param scores: the relevance scores for the skill valued [0;1]
        :return: a list of all query responses
        """
        logger.debug("Chose the following skill for the question '{}': {}".format(
            question, ", ".join(["{} ({:.4f})".format(skill["name"], score) for skill, score in zip(skills, scores)])))
        results = []
        count = len(skills)
        for skill_result in pool.imap(request_skill, repeat(question, count), repeat(options, count), skills, scores):
            results.append(skill_result)

    @staticmethod
    def query_skills_generator(question, options, skills, scores):
        """
        Query all skills in a given list asynchronously.
        The result are yielded as they come in.
        :param question: the question for the query
        :param options: the options for the query
        :param skills: the skills to query
        :param scores: the relevance scores for the skill valued [0;1]
        :return: a generator for a list of all query responses
        """
        logger.debug("Chose the following skill for the question '{}': {}".format(
            question, ", ".join(["{} ({:.4f})".format(skill["name"], score) for skill, score in zip(skills, scores)])))
        count = len(skills)
        for skill_result in pool.imap(request_skill, repeat(question, count), repeat(options, count), skills, scores):
            yield skill_result

    @staticmethod
    def _filter_unpublished_skills(skills):
        """
        Return a list with all skills that are not published removed
        :param skills: the skill list to filter
        :return: a list with all skills that are not published removed
        """
        return [skill for skill in skills if skill.is_published]


class BaseSelector(Selector):
    """
    A simple base selector that always choses the first maxQuerriedSkills skills in the options to query.
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

    def train(self, id, sentences):
        # BaseSelector needs no training.
        pass

    def unpublish(self, id):
        # BaseSelector needs no training so there is nothing to unpublish.
        pass


class ElasticsearchVoteSelector(Selector):
    """
    A simple base selector that always choses the first maxQuerriedSkills skills in the options to query.
    This selector can be used if a developer wants to query specific skills.
    """
    def __init__(self):
        super(ElasticsearchVoteSelector, self).__init__()

    def query(self, question, options, generator=False):
        skills = self._filter_unpublished_skills(options["selectedSkills"])
        scores = [1]*len(skills)
        if generator:
            return self.query_skills_generator(question, options, skills, scores)
        else:
            return self.query_skills(question, options, skills, scores)

    def train(self, id, sentences):
        # BaseSelector needs no training.
        pass

    def unpublish(self, id):
        # BaseSelector needs no training so there is nothing to unpublish.
        pass