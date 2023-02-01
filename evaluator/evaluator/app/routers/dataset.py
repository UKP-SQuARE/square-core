import logging
from typing import List

from fastapi import APIRouter

from evaluator.app.models import DataSet

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dataset")


@router.get(
    "",
    response_model=List[str],
)
async def get_datasets():
    """Returns a list of supported data sets."""
    datasets = [dataset.value for dataset in DataSet]

    logger.debug("get_datasets {datasets}".format(datasets=datasets))
    return datasets
