from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Path
from square_auth.auth import Auth

from skill_manager.core import tasks
from skill_manager.core.docker_client import SkillManagerDockerClient
from skill_manager.models.skill_deployment import SkillDeployment
from skill_manager.models.skill_template import SkillTemplate
from skill_manager.models.task import TaskStatus
from skill_manager.routers.skill_templates import (
    get_skill_template_by_id,
    get_skill_templates,
)

router = APIRouter(prefix="/deployments")

auth = Auth()


@router.get("/{id}", response_model=SkillDeployment)
async def get_deployment_by_id(
    skill_template_id=Path(..., alias="id"),
    skill_manager_docker_client: SkillManagerDockerClient = Depends(
        SkillManagerDockerClient
    ),
):
    container = skill_manager_docker_client.get_skill_template_container_by_id(
        skill_template_id
    )
    if container:
        deployed = True
        url = container.labels["url"]
    else:
        deployed = False
        url = None

    return SkillDeployment(
        skill_template_id=skill_template_id,
        deployed=deployed,
        url=url,
    )


@router.get("", response_model=List[SkillDeployment])
async def get_deployments(
    skill_manager_docker_client: SkillManagerDockerClient = Depends(
        SkillManagerDockerClient
    ),
):
    skill_templates: List[SkillTemplate] = await get_skill_templates()
    containers = skill_manager_docker_client.get_skill_template_containers()
    container_skill_template_ids = [
        c.labels.get("skill-template-id", "") for c in containers
    ]

    skill_deployments = []
    for skill_template in skill_templates:
        if skill_template.id in container_skill_template_ids:
            container_idx = container_skill_template_ids.index(skill_template.id)
            url = containers[container_idx].labels["url"]
            deployed = True
        else:
            url = None
            deployed = False
        skill_deployments.append(
            SkillDeployment(
                skill_template_id=str(skill_template.id),
                deployed=deployed,
                url=url,
            )
        )
    return skill_deployments


@router.post("/{id}", response_model=TaskStatus)
async def deploy_skill_template(skill_template_id=Path(..., alias="id")):
    skill_template = await get_skill_template_by_id(skill_template_id)
    result: AsyncResult = tasks.build_and_deploy_skill_template_container.delay(
        skill_template
    )

    return TaskStatus(task_id=result.id, status=result.status)
