import logging
import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

logger = logging.getLogger(__name__)


class TestcontainerKeycloak(DockerContainer):
    def __init__(self, image, **kwargs):
        super().__init__(image, **kwargs)
        self.port_to_expose = 8080
        self.with_exposed_ports(self.port_to_expose)
        self.with_env("KEYCLOAK_USER", kwargs.get("keycloak_user", "admin"))
        self.with_env("KEYCLOAK_PASSWORD", kwargs.get("keycloak_password", "admin"))

    @wait_container_is_ready()
    def _connect(self):
        connection_url = self.get_connection_url()
        response = requests.get(f"{connection_url}/auth", timeout=1)
        response.raise_for_status()

    def get_connection_url(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(8080)
        return f"http://{host}:{port}"

    def start(self):
        super().start()
        self._connect()
        return self
