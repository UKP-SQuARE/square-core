import json

from locust import between
from locust.contrib.fasthttp import FastHttpUser


def task_query(config, endpoint):
    """
    Template to make Locust tasks for queries that are generated dynamically based on the given config and endpoint.
    Locust calls its task functions only with the user as argument, so we create a closure and return it.

    :param config: the config for the task with the base URI, skill id, and the JSON input, etc.
    :param endpoint: the endpoint for the query
    :return: the closure for the Locust task function that makes the specified query
    """

    def query(user):
        base_path = config["base_uri"]
        if config["skill_id"]:
            path = base_path+"/{}/{}".format(config["skill_id"], endpoint)
            query_json = config["query_json"]
            user.client.post(path, json=query_json, name=config["name"])
        else:
            path = base_path
            user.client.get(path, name=config["name"])
    return query


class SkillAPIUser(FastHttpUser):
    wait_time = between(1, 2)
    tasks = []

    def __init__(self, *args, **kwargs):
        # Load config
        config = json.load(open("config.json"))
        general_config = config["config"]

        # Setup User
        wait_time = general_config.get("wait_time", [1, 2])
        # self.wait_time = between(...) does not work for some reason because it expects one argument that is not
        # used but not supplied in calls
        self.wait_time = lambda: between(wait_time[0], wait_time[1])(None)

        # Set up the Locust tasks
        tasks = []
        for task in config["tasks"]:
            task.update(general_config)
            task_function = task_query(task, task["endpoint"])
            for _ in range(task.get("weight", 1)):
                tasks.append(task_function)
        self.tasks = tasks

        super().__init__(*args, **kwargs)
