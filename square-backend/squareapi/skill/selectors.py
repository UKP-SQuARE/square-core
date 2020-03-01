import requests


class Selector:
    """
    Selector base class for all selector implementations
    """
    def query(self, question, options):
        """
        Answers a query with the skills chosen by the selector.
        :param question: the query question
        :param options: the options for the query
        :return:
        """
        raise NotImplementedError

    def requestSkill(self, question, options, skill):
        """
        Send a query request to a skill.
        maxResultsPerSkill is enforced by this method.
        :param question: the question for the query
        :param options: the options for the query
        :param skill: the skill to query
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
            return {"name": skill["name"], "skill_description": skill["description"], "results": r.json()[:maxResults]}
        except requests.Timeout as e:
            return {"name": skill["name"], "skill_description": skill["description"], "error": str(e)}
        except requests.ConnectionError as e:
            return {"name": skill["name"], "skill_description": skill["description"], "error": str(e)}

    def querySkills(self, question, options, skills):
        """
        Query all skills in a given list
        :param question: the question for the query
        :param options: the options for the query
        :param skills: the skills to query
        :return: a list of all query responses
        """
        result = []
        for skill in skills:
            result.append(self.requestSkill(question, options, skill))
        return result


class BaseSelector(Selector):
    """
    A simple base selector that always choses the first maxQuerriedSkills skills in the options to query.
    This selector can be used if a developer wants to query specific skills.
    """
    def __init__(self):
        super(BaseSelector, self).__init__()

    def query(self, question, options):
        skills = options["selectedSkills"][:int(options["maxQuerriedSkills"])]
        return self.querySkills(question, options, skills)
