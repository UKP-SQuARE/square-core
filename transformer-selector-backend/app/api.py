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
    try:
        await model_manager.train(id)
        return {"success": True, "msg": "ok"}
    except Exception as e:
        return {"success": False, "msg": repr(e)}

@api.post("/unpublish")
def scores(id: int):
    try:
        model_manager.unpublish(id)
        return {"success": True, "msg": "ok"}
    except Exception as e:
        return {"success": False, "msg": repr(e)}

@api.get("/ping")
def ping():
    return {"msg": "pong"}
