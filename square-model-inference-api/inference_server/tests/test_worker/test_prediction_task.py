from nose.tools import eq_

from square_model_inference.models.request import PredictionRequest
from tasks.tasks import prediction_task
import celery

celery.conf.task_always_eager = False


def test_add_task():
    request = PredictionRequest(input=["Some text"])
    task = "embedding"
    model_config = {"identifier": "facebook-dpr-question_encoder-single-nq-base",
        "model_type": "transformer",
        "model_name": "facebook/dpr-question_encoder-single-nq-base",
        "disable_gpu": False,
        "batch_size": 32,
        "max_input": 1024,
        "model_class": "base",
        "return_plaintext_arrays": False
    }
    rst = prediction_task.apply_async(args=(request, task, model_config), queue="facebook-dpr-question_encoder-single-nq-base").get()
    eq_(rst, 8)