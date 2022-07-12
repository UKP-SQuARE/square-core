import logging
import os
import re

import docker
from docker.types import Mount


logger = logging.getLogger(__name__)

docker_client = docker.from_env()

MODEL_API_IMAGE = os.getenv("MODEL_API_IMAGE", "ukpsquare/square-model-api-v1.1:latest")
ONNX_VOLUME = os.getenv("ONNX_VOLUME", "square-model-inference-api_onnx-models")
MODELS_API_PATH = "models"  # For management server e.g. /api/models/deployed-models to list models etc.


def create_docker_labels(identifier: str, uid: str) -> dict:
    """
    creates the labels to enable traefik for the docker container
    """
    traefik_identifier = identifier.replace("/", "-") + uid
    labels = {
        "traefik.enable": "true",
        "traefik.http.routers.model-" + traefik_identifier + ".rule": "PathPrefix(`/api/" + identifier + "`)",
        "traefik.http.routers.model-" + traefik_identifier + ".entrypoints": "websecure",
        "traefik.http.routers.model-" + traefik_identifier + ".tls": "true",
        "traefik.http.routers.model-" + traefik_identifier + ".tls.certresolver": "le",
        "traefik.http.routers.model-"
        + traefik_identifier
        + ".middlewares": "model-"
        + traefik_identifier
        + "-stripprefix, "
        + "model-"
        + traefik_identifier
        + "-addprefix",
        "traefik.http.middlewares.model-" + traefik_identifier + "-stripprefix.stripprefix.prefixes": "/api/" + identifier,
        "traefik.http.middlewares.model-" + traefik_identifier + "-addprefix.addPrefix.prefix": "/api",
    }
    return labels


def start_new_model_container(identifier: str, uid: str, env):
    """
    Start a new container in the current network with a new model-api instance.
    identifier(str): the name/identifier of the new model api instance
    env(Dict): the environment for the container
    """
    container = get_container_by_identifier(identifier, uid)
    if container is not None:
        logger.info("Found old container for that identifier container")
        logger.info(container.status)
        if container.status == "running":
            return {
                "container": container,
                "message": "A container wth same name is already deployed",
            }
        logger.info("Removing old container")
        container.stop()
        container.remove()
    else:
        logger.info("Found no running instance, so we try to create it")
    labels = create_docker_labels(identifier, uid=uid)
    # in order to obtain necessary information like the network id
    # get the traefik container and read out the information
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    logger.info("Refernce Container: {}".format(reference_container))
    network_id = list(reference_container.attrs["NetworkSettings"]["Networks"].values())[0]["NetworkID"]

    path = ":".join(reference_container.attrs["HostConfig"]["Binds"][1].split(":")[:-2])
    # in case of windows the next step is necessary
    path = path.replace("\\", "/")
    path = os.path.dirname(os.path.dirname(path))

    network = docker_client.networks.get(network_id)
    container_name = network.name + "-model-" + identifier.replace("/", "-") + uid
    logger.info("Container name of model: {}".format(container_name))

    try:
        kwargs = dict(
            image=MODEL_API_IMAGE,
            name=container_name,
            detach=True,
            environment=env,
            network=network.name,
            # volumes=[path + "/.cache/:/etc/huggingface/.cache/"], # DO NOT COMMIT!
            volumes=["/Users/tim/projects/square/square-core/.cache/:/etc/huggingface/.cache/"],
            mounts=[
                Mount(
                    target="/onnx_models",
                    source=ONNX_VOLUME,
                )
            ],
            labels=labels,
        )
        logger.info("docker run kwargs: {}".format(kwargs))
        container = docker_client.containers.run(**kwargs)

        network.reload()
    except Exception as e:
        logger.exception(e, exc_info=True)
        return {"container": None, "message": f"Caught exception. {e}"}
    return {"container": container, "message": "Success"}


def get_container_by_identifier(identifier: str, uid: str):
    """
    get the docker container based on the model identifier
    """
    labels = create_docker_labels(identifier, uid)
    if (
        len(
            docker_client.containers.list(
                all=True, filters={"label": [f"{k}={v}" for k, v in labels.items()]}
            )
        )
        == 0
    ):
        return None
    container = docker_client.containers.list(
        all=True, filters={"label": [f"{k}={v}" for k, v in labels.items()]}
    )[0]
    return container


def get_container(container_id):
    """
    get the docker container based on its id
    """
    if len(docker_client.containers.list(all=True, filters={"id": container_id})) == 0:
        return None
    container = docker_client.containers.list(all=True, filters={"id": container_id})[0]
    return container


def remove_model_container(container_id):
    """
    Removes container for the given identifier
    """
    container = get_container(container_id)
    if container is None:
        return False
    container.stop()
    container.remove()

    return True


def get_all_model_prefixes():
    """
    Returns the prefixes under which all running model-api-instances in the docker-network are available
    """
    # assumes square is somewhere in the container name
    lst_container = docker_client.containers.list(filters={"name": "square"})
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    port = list(reference_container.attrs["NetworkSettings"]["Ports"].items())[0][1][0]["HostPort"]

    lst_prefix = []
    lst_container_ids = []
    for container in lst_container:
        logger.debug("Found candidate model container: %s", container.name)
        if "model" in container.name:
            for _, label in container.labels.items():
                if "PathPrefix" in label and MODELS_API_PATH not in label:
                    prefix = re.search(r"PathPrefix\(`(.+?)`\)", label).group(1)
                    lst_prefix.append(prefix)
                    lst_container_ids.append(container.id)

    logger.debug("Found model containers: %s on port %s", lst_prefix, port)
    return lst_prefix, lst_container_ids, port


def get_port():
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    return list(reference_container.attrs["NetworkSettings"]["Ports"].items())[0][1][0]["HostPort"]
