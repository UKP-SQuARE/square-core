import requests


class Selector:
    def query(self, question, options):
        raise NotImplementedError

    def requestSkill(self, question, options, skill):
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
        result = []
        for skill in skills:
            result.append(self.requestSkill(question, options, skill))
        return result


class BaseSelector(Selector):
    def __init__(self):
        super(BaseSelector, self).__init__()

    def query(self, question, options):
        skills = options["selectedSkills"][:int(options["maxQuerriedSkills"])]
        return self.querySkills(question, options, skills)
