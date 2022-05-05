import dill as pickle
from square_skill_api import get_app

with open("skill_template.pickle", "rb") as fn:
    predict = pickle.load(fn)

app = get_app(predict_fn=predict)
