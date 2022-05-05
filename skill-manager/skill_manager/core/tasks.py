import os

from celery import Celery
from docker.models.containers import Container
from skill_manager.core.docker_client import SkillManagerDockerClient

from skill_manager.models.skill_template import SkillTemplate
from skill_manager.models.skill_deployment import SkillDeployment

rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "ukp")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "secret")

redis_user = os.getenv("REDIS_USER", "ukp")
redis_password = os.getenv("REDIS_PASSWORD", "secret")

app = Celery(
    "tasks",
    backend=f"redis://{redis_user}:{redis_password}@redishost:6379",
    broker=f"amqp://{rabbitmq_user}:{rabbitmq_password}@rabbit:5672//",
    include=["tasks.tasks"],
)


@app.task()
def build_and_deploy_skill_template_container(
    skill_template: SkillTemplate, docker_client: SkillManagerDockerClient
):

    docker_client.build_skill_template(skill_template.id)

    container: Container = docker_client.deploy_skill_template(
        skill_template, network_ref_container_name="traefik", wait=True
    )

    return SkillDeployment(
        skill_template_id=str(skill_template.id),
        deployed=True,
        url=container.labels["url"]
    )
