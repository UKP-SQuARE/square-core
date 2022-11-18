import logging
from typing import List

from fastapi import APIRouter

from skill_manager.models import DataSet

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-sets")


@router.get(
    "",
    response_model=List[str],
)
async def get_data_sets():
    """Returns a list of supported data sets."""
    data_sets = [data_set.value for data_set in DataSet]

    logger.debug("get_data_sets {data_sets}".format(data_sets=data_sets))
    return data_sets
