import logging
from abc import ABC

import requests
import time
import asyncio
import os
from celery import Task
from .celery import app
from docker_access import start_new_model_container, get_all_model_prefixes, remove_model_container, get_port
from mongo_access import MongoClass
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelTask(Task, ABC):
    """
    Abstraction of Celery's Task class to support providing mongo client.
    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.client = None

    def __call__(self, *args, **kwargs):
        """
        Instantiate mongo client on first call (i.e. first task processed)
        Avoids the creation of multiple clients for each task request
        """
        if not self.client:
            logging.info('Instantiating Mongo Client...')
            self.client = MongoClass()
        return self.run(*args, **kwargs)

@app.task(
    bind=True,
    base=ModelTask,
)
def deploy_task(self, identifier, env):
    try:
        self.client.server_info()
    except Exception as e:
        logger.exception(e)
        return {
                "success": False,
                "message": "Connection to the database failed."
            }
    logger.debug(env)
    try:
        container = start_new_model_container(identifier, env)
        logger.debug(container)
        if container is not None:
            result = {
                "success": True,
                "container": container.id,
                "message": "Model deployed. Check the `/api/models/deployed-models` "
                           "endpoint for more info."
            }
            response = None
            while container.status in ["created", "running"] and (response is None or response.status_code != 200):
                time.sleep(20)
                logger.info(f"Waiting for container {container.id} which is {container.status}")
                response = requests.get(
                    url="{}/api/{}/stats".format(settings.API_URL, identifier),
                    verify=os.getenv("VERIFY_SSL", 1) == 1,
                )

                if response.status_code == 200:
                    asyncio.run(self.client.add_model_db(identifier, env))
                    return result
            return {
                "success": False,
                "container_status": container.status,
            }
    except Exception as e:
        logger.exception("Deployment failed", exc_info=True)
        logger.info("Caught exception. {} ".format(e))
    return {"success": False}


@app.task(
    bind=True,
    base=ModelTask,
)
def remove_model_task(self, identifier):
    try:
        self.client.server_info()
    except:
        return {
                "success": False,
                "message": "Connection to the database failed."
            }
    try:
        result = remove_model_container(identifier)
        if result:
            asyncio.run(self.client.remove_model_db(identifier))
            return {
                "success": result,
                "message": "Model removal successful"
            }
    except:
        logger.exception("Could not remove model", exc_info=True)
    return {
        "success": False,
        "message": "Model removal not successful"
    }