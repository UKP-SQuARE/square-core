from fastapi import APIRouter
from .transformer.model import ModelManager


def _to_result(text):
    return {"type": "plain_text", "result": text}


api = APIRouter()
model_manager = ModelManager()


@api.get("/scores")
async def scores(question: str):
    results = await model_manager.scores(question)
    return results


@api.post("/train")
async def train(id: int):
    await model_manager.train(id)
    return {"msg": "ok"}


@api.post("/unpublish")
def scores(id: int):
    model_manager.unpublish(id)
    return {"msg": "ok"}
