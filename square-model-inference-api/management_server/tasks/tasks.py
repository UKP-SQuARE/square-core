import logging
from .celery import app
from docker_access import start_new_model_container, get_all_model_prefixes, remove_model_container


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
                "message": "Model deployment in progress. Check the `/api/models/deployed-models` "
                           "endpoint for more info."
            }
            return result
    except:
        logger.exception("Deployment failed", exc_info=True)
    return {"success": False}


@app.task
def remove_model_task(identifier):
    try:
        result = remove_model_container(identifier)
        if result:
            return {
                "success": result,
                "message": "Model removal successful"
            }
    except:
        logger.exception("Could not remove model", exc_info=True)