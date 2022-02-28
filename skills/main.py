import logging

from square_skill_api import get_app
from skill import predict

logger = logging.getLogger(__name__)

app = get_app(predict_fn=predict)
