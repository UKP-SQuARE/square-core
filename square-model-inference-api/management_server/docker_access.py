import os
import re
import logging

logger = logging.getLogger(__name__)

import docker
from docker.types import Mount

docker_client = docker.from_env()

MODEL_API_IMAGE = os.getenv("MODEL_API_IMAGE", "ukpsquare/square-model-api-v1:latest")
ONNX_VOLUME = os.getenv("ONNX_VOLUME", "square-model-inference-api_onnx-models")
MODELS_API_PATH = "models"  # For management server e.g. /api/models/deployed-models to list models etc.


def start_new_model_container(identifier, env):
    """
    Start a new container in the current network with a new model-api instance.
    identifier(str): the name/identifier of the new model api instance
    env(Dict): the environment for the container
    """
    labels = {
        "traefik.enable": "true",
        "traefik.http.routers.model-" + identifier + ".rule": "PathPrefix(`/api/" + identifier + "`)",
        "traefik.http.routers.model-" + identifier + ".entrypoints": "websecure",
        "traefik.http.routers.model-" + identifier + ".tls": "true",
        "traefik.http.routers.model-" + identifier + ".tls.certresolver": "le",
        "traefik.http.routers.model-" + identifier + ".middlewares": "model-" + identifier + "-stripprefix, " + "model-"\
                                                                     + identifier + "-addprefix",
        "traefik.http.middlewares.model-" + identifier + "-stripprefix.stripprefix.prefixes": "/api/" + identifier,
        "traefik.http.middlewares.model-" + identifier + "-addprefix.addPrefix.prefix": "/api",
    }
    # in order to obtain necessary information like the network id
    # get the traefik container and read out the information
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    network_id = list(reference_container.attrs['NetworkSettings']['Networks'].values())[0]['NetworkID']

    path = ":".join(reference_container.attrs['HostConfig']['Binds'][1].split(":")[:-2])
    # in case of windows the next step is necessary
    path = path.replace("\\", "/")
    path = os.path.dirname(os.path.dirname(path))

    network = docker_client.networks.get(network_id)
    container_name = network.name + "-model-" + identifier

    try:
        container = docker_client.containers.run(
            MODEL_API_IMAGE,
            name=container_name,
            detach=True,
            environment=env,
            network=network.name,
            volumes=[path + "/.cache/:/etc/huggingface/.cache/"],
            mounts=[Mount(target="/onnx_models", source=ONNX_VOLUME, )],
            labels=labels,
        )

        network.reload()
    except:
        return None
    return container


def remove_model_container(identifier):
    """
    Removes container for the given identifier
    """

    labels = {
        "traefik.enable": "true",
        "traefik.http.routers.model-" + identifier + ".rule": "PathPrefix(`/api/" + identifier + "`)",
        "traefik.http.routers.model-" + identifier + ".entrypoints": "websecure",
        "traefik.http.routers.model-" + identifier + ".tls": "true",
        "traefik.http.routers.model-" + identifier + ".tls.certresolver": "le",
        "traefik.http.routers.model-" + identifier + ".middlewares": "model-" + identifier + "-stripprefix, " + "model-" \
                                                                     + identifier + "-addprefix",
        "traefik.http.middlewares.model-" + identifier + "-stripprefix.stripprefix.prefixes": "/api/" + identifier,
        "traefik.http.middlewares.model-" + identifier + "-addprefix.addPrefix.prefix": "/api",
    }

    if len(docker_client.containers.list(filters={"label": ["{}={}".format(k, v) for k, v in labels.items()]})) == 0:
        return False
    container = docker_client.containers.list(filters={"label": ["{}={}".format(k, v) for k, v in labels.items()]})[0]
    container.stop()
    container.remove()

    return len(docker_client.containers.list(filters={"label": ["{}={}".format(k, v) for k, v in labels.items()]})) == 0


def get_all_model_prefixes():
    """
    Returns the prefixes under which all running model-api-instances in the docker-network are available
    """
    # assumes square is somewhere in the container name
    lst_container = docker_client.containers.list(filters={"name": "square"})
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    port = list(reference_container.attrs["NetworkSettings"]["Ports"].items())[0][1][0]["HostPort"]

    lst_prefix = []
    for container in lst_container:
        logger.debug(f"Found candidate model container: {container.name}")
        if "model" in container.name:
            for identifier, label in container.labels.items():
                if "PathPrefix" in label and MODELS_API_PATH not in label:
                    prefix = re.search('PathPrefix\(\`(.+?)\`\)', label).group(1)
                    lst_prefix.append(prefix)

    logger.debug(f"Found model containers: {lst_prefix} on port {port}")
    return lst_prefix, port


def get_port():
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    return list(reference_container.attrs["NetworkSettings"]["Ports"].items())[0][1][0]["HostPort"]