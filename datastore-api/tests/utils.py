import os
import time
from typing import Dict, Optional
import docker
from docker.models.containers import Container
import requests
import tqdm


def start_container(
    image: str,
    port_host: int,
    port_container: int,
    network: str,
    name: str,
    mem_limit: str = "512m",
    envs: Optional[Dict[str, str]] = None,
) -> Container:
    client = docker.from_env()
    container: Container
    for container in client.containers.list():
        if container.name == name:
            print(f"Found existing container {container.id}. Now restart it")
            container.remove(force=True)
            break
    environment = {"transport.host": "127.0.0.1", "http.host": "0.0.0.0"}
    if envs:
        environment.update(envs)
    container = client.containers.run(
        image=image,
        name=name,
        network=network,
        mem_limit=mem_limit,
        remove=True,
        detach=True,
        environment=environment,
        ports={f"{port_host}/tcp": port_container},
    )
    return container


def wait_for_up(url: str, ntries=100) -> None:
    for _ in tqdm.trange(ntries, desc=f"Waiting for {url} up"):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                break
        except:
            time.sleep(1)

def inside_container() -> bool:
    """
    Returns true if we are running inside a container.

    https://github.com/docker/docker/blob/a9fa38b1edf30b23cae3eade0be48b3d4b1de14b/daemon/initlayer/setup_unix.go#L25
    """
    return os.path.exists('/.dockerenv')
