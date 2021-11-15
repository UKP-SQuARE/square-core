import logging

from square_skill_api import get_app
from skillapi.skill import predict

logger = logging.getLogger(__name__)

app = get_app(predict_fn=predict)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
