import logging

from skill import predict
from square_skill_api import get_app

logger = logging.getLogger(__name__)

app = get_app(predict_fn=predict)
