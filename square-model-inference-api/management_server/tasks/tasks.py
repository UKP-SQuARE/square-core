import asyncio
import logging
import os
import time
from abc import ABC

import requests
from celery import Task

from app.core.config import settings
from app.routers import client_credentials
from docker_access import remove_model_container, start_new_model_container
from mongo_access import MongoClass

from .celery import app


logger = logging.getLogger(__name__)


class ModelTask(Task, ABC):
    """
    Abstraction of Celery's Task class to support providing mongo client.
    """

    abstract = True

    def __init__(self):
        super().__init__()
        self.client = None
        self.credentials = None

    def __call__(self, *args, **kwargs):
        """
        Instantiate mongo client on first call (i.e. first task processed)
        Avoids the creation of multiple clients for each task request
        """
        if not self.client:
            logging.info("Instantiating Mongo Client...")
            self.client = MongoClass()

        if not self.credentials:
            self.credentials = client_credentials
        return self.run(*args, **kwargs)


@app.task(
    bind=True,
    base=ModelTask,
)
def deploy_task(self, env, allow_overwrite=False):
    """
    deploy model to the platform
    """
    logger.info(env)
    identifier = env["IDENTIFIER"]
    try:
        self.client.server_info()
    except Exception as e:
        logger.exception(e)
        return {"success": False, "message": "Connection to the database failed."}
    try:
        deployment_result = start_new_model_container(identifier, env)
        container = deployment_result["container"]
        # models = asyncio.run(self.client.get_models_db())
        # model_ids = [m["IDENTIFIER"] for m in models]
        if container is not None:  # and identifier not in model_ids:
            result = {
                "success": True,
                "container": container.id,
                "message": "Model deployed. Check the `/api/models/deployed-models` " "endpoint for more info.",
            }
            response = None
            while container.status in ["created", "running"] and (response is None or response.status_code != 200):
                time.sleep(20)
                logger.info("Waiting for container %s which is %s", container.id, container.status)
                response = requests.get(
                    url=f"{settings.API_URL}/api/{identifier}/stats",
                    headers={"Authorization": f"Bearer {self.credentials()}"},
                    verify=os.getenv("VERIFY_SSL", 1) == 1,
                )

                if response.status_code == 200:
                    logger.info(env)
                    env["container"] = container.id
                    asyncio.run(self.client.add_model_db(env, allow_overwrite))
                    return result
            logger.info(container.status)
            logger.info(response.status_code)
            return {
                "success": False,
                "container_status": container.status,
            }

    except Exception as e:
        logger.exception("Deployment failed", exc_info=True)
        logger.info("Caught exception. %s ", e)

    return {"success": False}


@app.task(
    bind=True,
    base=ModelTask,
)
def remove_model_task(self, identifier):
    """
    Remove model from the platform
    """
    try:
        self.client.server_info()
    except Exception:
        return {"success": False, "message": "Connection to the database failed."}
    try:
        container_id = self.client.get_container_id(identifier)
        logger.info("Starting to remove docker container %s", container_id)
        result = remove_model_container(container_id)
        if result:
            asyncio.run(self.client.remove_model_db(identifier))
            return {"success": result, "message": "Model removal successful"}
    except Exception as e:
        logger.info(e)
        logger.exception("Could not remove model", exc_info=True)
    return {"success": False, "message": "Model removal not successful"}
