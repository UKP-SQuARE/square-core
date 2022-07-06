import os
import shutil
from contextlib import contextmanager
from time import time
from typing import List, Union

from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image

from skill_manager.models.skill_template import SkillTemplate


class SkillManagerDockerClient:
    def __init__(self) -> None:
        self.docker_client = DockerClient.from_env()

    @contextmanager
    def _copy_remove_file(self, source, destination):
        if not os.path.isfile(source):
            raise FileNotFoundError(source)
        if os.path.isdir(destination):
            raise RuntimeError(
                f"Destination must be a file path, but got {destination}."
            )
        shutil.copy(source, destination)
        yield
        os.remove(destination)

    def build_skill_template(
        self, pickle_path: str, skill_template_docker_dir: str, skill_template_id: str
    ) -> Image:
        with self._copy_remove_file(
            pickle_path,
            os.path.join(skill_template_docker_dir, f"{skill_template_id}.pickle"),
        ):
            image, build_logs = self.docker_client.images.build(
                path=skill_template_docker_dir,
                tag=f"ukpsquare/skill-template-{skill_template_id}",
                buildargs={"skill_template_pickle": f"{skill_template_id}.pickle"},
            )
        return image

    def _get_network(self, ref_container_name: str = "traefik"):
        ref_container = self.docker_client.containers.list(
            filters={"name": ref_container_name}
        )[0]
        network_id = list(ref_container.attrs["NetworkSettings"]["Networks"].values())
        network_id = network_id[0]["NetworkID"]
        network = self.docker_client.networks.get(network_id)

        return network

    def deploy_skill_template(
        self, skill_template: SkillTemplate, network_ref_container_name: str, wait=True
    ) -> Container:

        skill_template_id = skill_template.id

        container: Container = self.docker_client.containers.run(
            f"ukpsquare/skill-template-{skill_template_id}",
            detach=True,
            publish_all_ports=True,
            network=self._get_network(network_ref_container_name).name,
            environment={
                "WEB_CONCURRENCY": os.getenv("SKILL_WEB_CONCURRENCY", 2),
                "VERIFY_SSL": os.getenv("SKILL_VERIFY_SSL", 1),
                "SQUARE_API_URL": os.environ["SQUARE_API_URL"],
                "KEYCLOAK_BASE_URL": os.environ["KEYCLOAK_BASE_URL"],
                "REALM": os.environ["REALM"],
                "CLIENT_ID": skill_template.client_id,
            },
            labels={
                "skill-template-id": skill_template_id,
                "type": "skill-template",
                "url": f"/api/skill-templates/{skill_template_id}",
                "traefik.enable": "true",
                f"traefik.http.routers.{skill_template_id}.rule": f"PathPrefix(`/api/skill-templates/{skill_template_id}`)",
                f"traefik.http.routers.{skill_template_id}.middlewares": f"{skill_template_id}-stripprefix,{skill_template_id}-addprefix",
                f"traefik.http.middlewares.{skill_template_id}-stripprefix.stripprefix.prefixes": "/api/skill-templates/{skill_template_id}",
                f"traefik.http.middlewares.{skill_template_id}-addprefix.addPrefix.prefix": f"/api",
            },
        )

        if wait:
            self._wait_for_container_status(container, "running")

        return container

    def _wait_for_container_status(
        self, container: Container, target_status: str, attempts: int = 60
    ):
        while attempts > 0:
            container.reload()
            if container.status == target_status:
                return
            time.sleep(1)
            attempts -= 1

        raise RuntimeError(
            f"Container status {target_status} not reached. Status={container.status()}"
        )

    def get_skill_template_containers(self) -> List[Container]:
        return self.docker_client.containers.list(
            filters={"label": "type=skill-template"}
        )

    def get_skill_template_container_by_id(
        self, skill_template_id
    ) -> Union[Container, None]:
        skill_template_container = self.docker_client.containers.list(
            filters={"label": f"skill-template-id={skill_template_id}"}
        )
        if skill_template_container:
            skill_template_container = skill_template_container[0]
        else:
            skill_template_container = None

        return skill_template_container
