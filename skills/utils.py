from typing import Dict

from square_skill_api.models import QueryRequest


def extract_model_kwargs_from_request(request: QueryRequest) -> Dict[str, Dict]:
    """Extracts the kwargs from a QueryRequest"""

    return {
        "explain_kwargs": request.explain_kwargs or {},
        "attack_kwargs": request.attack_kwargs or {},
        "model_kwargs": request.model_kwargs or {},
        "task_kwargs": request.task_kwargs or {},
        "preprocessing_kwargs": request.skill_args["preprocessing_kwargs"] or {},
    }
