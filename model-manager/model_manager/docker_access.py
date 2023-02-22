import logging
import os
import random
from multiprocessing import cpu_count

import docker
from docker.types import Mount


logger = logging.getLogger(__name__)

docker_client = docker.from_env()


ONNX_VOLUME = os.getenv("ONNX_VOLUME", "model-inference_onnx-models")
CONFIG_VOLUME = os.getenv("CONFIG_VOLUME", "model-inference_model_configs")
MODELS_API_PATH = "models"  # For management server e.g. /api/models/deployed-models to list models etc.
USER = os.getenv("USERNAME", "user")
PASSWORD = os.getenv("PASSWORD", "user")


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
    # in order to obtain necessary information like the network id
    # get the traefik container and read out the information
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    logger.info("Reference Container: {}".format(reference_container))
    network_id = list(reference_container.attrs["NetworkSettings"]["Networks"].values())[0]["NetworkID"]

    # path = ":".join(reference_container.attrs["HostConfig"]["Binds"][1].split(":")[:-2])
    # logger.info("Path: {}".format(path))
    # # in case of windows the next step is necessary
    # path = path.replace("\\", "/")
    # path = os.path.dirname(os.path.dirname(path))

    network = docker_client.networks.get(network_id)
    worker_name = network.name + "-model-" + identifier.replace("/", "-") + "-worker-" + uid

    env["WEB_CONCURRENCY"] = 1
    env["KEYCLOAK_BASE_URL"] = os.getenv("KEYCLOAK_BASE_URL", "https://square.ukp-lab.de")
    env["QUEUE"] = identifier.replace("/", "-")
    env["RABBITMQ_DEFAULT_USER"] = os.getenv("RABBITMQ_DEFAULT_USER", "ukp")
    env["RABBITMQ_DEFAULT_PASS"] = os.getenv("RABBITMQ_DEFAULT_PASS", "secret")

    env["REDIS_USER"] = os.getenv("REDIS_USER", "ukp")
    env["REDIS_PASSWORD"] = os.getenv("REDIS_PASSWORD", "secret")
    env["CONFIG_PATH"] = os.getenv("CONFIG_PATH", "/model_configs")

    model_api_base_image = os.getenv("MODEL_API_IMAGE", "ukpsquare/model-inference")
    image_tag = os.getenv("MODEL_API_IMAGE_TAG", "latest")

    image = ""
    # select the image based on the model type
    if env["MODEL_TYPE"] in ["transformer","adapter","metaqa"]:
        image = f"{model_api_base_image}-transformer:{image_tag}"
    if env["MODEL_TYPE"] in ["sentence-transformer"]:
        image = f"{model_api_base_image}-sentence-transformer:{image_tag}"
    if env["MODEL_TYPE"] in ["graph-transformer"]:
        image = f"{model_api_base_image}-graph-transformer:{image_tag}"
    if env["MODEL_TYPE"] in ["onnx"]:
        image = f"{model_api_base_image}-onnx:{image_tag}"

    logger.info("Starting container with image: {}".format(image))


    try:
        random_cpus = random.sample(list(range(cpu_count())), k=os.getenv("CPU_COUNT", cpu_count() // 8))
        random_cpus = ",".join(map(str, random_cpus))
        cpuset_cpus = env.get("CPUS", random_cpus)
        logger.info(f"Deploying {identifier} using CPUS={cpuset_cpus}")
        logger.info(f"CONFIG_VOLUME={CONFIG_VOLUME}")
        container = docker_client.containers.run(
            image,
            command=f"celery -A tasks worker -Q {identifier.replace('/', '-')} --loglevel=info",
            name=worker_name,
            cpuset_cpus=cpuset_cpus,
            detach=True,
            environment=env,
            network=network.name,
            volumes=["/:/usr/src/app", "/var/run/docker.sock:/var/run/docker.sock"],
            mounts=[
                Mount(target=env["CONFIG_PATH"], source=CONFIG_VOLUME,),
                # Mount(target="/onnx_models", source=ONNX_VOLUME,)   # shouldn't be necessary for new ONNX version
            ],
        )
        logger.info(f"Worker container {container}")
        network.reload()
        entries_to_remove = ["RABBITMQ_DEFAULT_USER", "RABBITMQ_DEFAULT_PASS", "REDIS_USER", "REDIS_PASSWORD"]
        for k in entries_to_remove:
            env.pop(k, None)
    except Exception as e:
        logger.exception(e, exc_info=True)
        return {"container": None, "message": f"Caught exception. {e}"}
    return {"container": container, "message": "Success"}


def get_container_by_identifier(identifier: str, uid: str):
    """
    get the docker container based on the model identifier
    """
    labels = create_docker_labels(identifier, uid=uid)
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
            for env_var in container.attrs["Config"]["Env"]:
                if "QUEUE" in env_var:
                    logger.info(env_var)
                    key, val = env_var.split("=")
                    if "QUEUE" == key:
                        lst_prefix.append(val)
                        lst_container_ids.append(container.id)
                # maybe we can achieve this by finding the container with the same queue name

    logger.debug("Found model containers: %s on port %s", lst_prefix, port)
    return lst_prefix, lst_container_ids, port


def get_port():
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    return list(reference_container.attrs["NetworkSettings"]["Ports"].items())[0][1][0]["HostPort"]
