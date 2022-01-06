import docker
import os
import re

docker_client = docker.from_env()


async def start_new_model_container(identifier, env):
    """
    Start a new container in the current network with a new model-api instance.
    identifier(str): the name/identifier of the new model api instance
    env(Dict): the environment for the container
    """
    labels = {
        "traefik.enable": "true",
        "traefik.http.routers." + identifier + ".rule": "PathPrefix(`/api/" + identifier + "`)",
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
    container_name = network.name + "_" + identifier
    try:
        container = docker_client.containers.run(
            "ukpsquare/square-model-api:latest",
            name=container_name,
            detach=True,
            environment=env,
            network=network.name,
            volumes=[path + "/.cache/:/etc/huggingface/.cache/"],
            labels=labels,
        )

        network.reload()
    except:
        return None
    return container


async def get_all_model_prefixes():
    """
    Returns the prefixes under which all running model-api-instances in the dockernetwor are available
    """
    # assumes square is somewhere in the container name
    lst_container = docker_client.containers.list(filters={"name": "square"})
    reference_container = docker_client.containers.list(filters={"name": "traefik"})[0]
    port = list(reference_container.attrs["NetworkSettings"]["Ports"].items())[0][1][0]["HostPort"]
    lst_prefix = []
    for container in lst_container:
        if "maintaining" not in container.name:
            for identifier, label in container.labels.items():
                if "PathPrefix" in label:
                    prefix = re.search('PathPrefix\(\`(.+?)\`\)', label).group(1)
                    lst_prefix.append(prefix)
    return lst_prefix, port
