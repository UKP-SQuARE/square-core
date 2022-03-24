import logging
import requests
import time
import asyncio
import os
from .celery import app
from docker_access import start_new_model_container, get_all_model_prefixes, remove_model_container, get_port
from mongo_access import add_model_db, remove_model_db, get_models_db, update_model_db, init_db, check_identifier_new
from app.core.config import settings

logger = logging.getLogger(__name__)


@app.task
def deploy_task(identifier, env):
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
                response = requests.get(
                    url="{}/api/{}/stats".format(settings.API_URL, identifier),
                    verify=os.getenv("VERIFY_SSL", 1) == 1,
                )

                if response.status_code == 200:
                    asyncio.run(add_model_db(identifier, env))
                    return result
            return {
                "success": False,
                "container_status": container.status,
            }
    except Exception as e:
        logger.exception("Deployment failed", exc_info=True)
        logger.info("Caught exception. {} ".format(e))
    return {"success": False}


@app.task
def remove_model_task(identifier):
    try:
        result = remove_model_container(identifier)
        if result:
            asyncio.run(remove_model_db(identifier))
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