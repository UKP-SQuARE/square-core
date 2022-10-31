import json

from locust import between
from locust.contrib.fasthttp import FastHttpUser


def task_query(config, endpoint):
    """
    Template to make Locust tasks for queries that are generated dynamically based on the given config and endpoint.
    Locust calls its task functions only with the user as argument, so we create a closure and return it.

    :param config: the config for the task with the model name, the API-Key, the JSON input, etc.
    :param endpoint: the endpoint for the query
    :return: the closure for the Locust task function that makes the specified query
    """

    def query(user):
        path = f"/api/{config['model']}/{endpoint}"
        query_json = config["query_json"]
        # headers = {config.get("api_key_header", "Authorization"): config["api_key"]}
        user.client.post(path, json=query_json)  # , headers=headers)

    return query


class ModelAPIUser(FastHttpUser):
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

        # Setup the Locust tasks
        tasks = []
        for task in config["tasks"]:
            task.update(general_config)
            # Endpoint in URL uses - instead of _, so we replace it in case config was wrong
            task_function = task_query(task, task["endpoint"].replace("_", "-"))
            for _ in range(task.get("weight", 1)):
                tasks.append(task_function)
        self.tasks = tasks

        super().__init__(*args, **kwargs)
