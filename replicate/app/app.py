import uvicorn
import argparse
import json

from fastapi import FastAPI, Request, APIRouter, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2.exceptions import TemplateError
from replicate.client import Client
from replicate.exceptions import ReplicateError
from jinja2 import Template


router = APIRouter()
with open('chat_templates.json', 'r') as file:
    chat_templates = json.load(file)

with open('models.json', 'r') as file:
    models = json.load(file)['models']


def default_formatter(messages):
    formatted = []
    for message in messages:
        if message["role"] == "user":
            formatted.append(f"User: {message['content']}")
        elif message["role"] == "assistant":
            formatted.append(f"Assistant: {message['content']}")
        elif message["role"] == "system":
            formatted.append(f"System: {message['content']}")
    formatted.append("Assistant: ")
    return "\n\n".join(formatted)


def hf_format(messages):
    for message in messages:
        if message["role"] == "human":
            message["role"] = "user"
        elif message["role"] == "ai":
            message["role"] = "assistant"
        if "text" in message:
            message["content"] = message.pop("text")
    return messages


def get_conversation_prompt(params) -> str:
    model = params["model_identifier"]
    messages = hf_format(params["messages"])
    formatted_prompt = ""

    if model in chat_templates:
        template = Template(chat_templates[model])
        try:
            formatted_prompt = template.render(messages=messages)
        except TemplateError:
            # remove system message
            new_messages = [message for message in messages if message["role"] != "system"]
            formatted_prompt = template.render(messages=new_messages)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error rendering template: " + str(e))
    elif model in models:  # default formatter in casen of unknown model
        formatted_prompt = default_formatter(messages)
    else:
        raise HTTPException(status_code=400, detail="Model identifier not supported.")

    return formatted_prompt


def get_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return authorization.split(" ")[1]


@router.get("/test")
async def api_test():
    return JSONResponse({"test": "test"})


@router.get("/models")
async def get_models():
    # from hf_rp_map return list of the keys
    return JSONResponse({"models": models})


@router.post("/generate_chat_stream")
async def generate_stream(request: Request, token: str = Depends(get_token)):
    params = await request.json()
    replicate = Client(api_token=token)
    model = params['model_identifier']

    formatted_prompt = get_conversation_prompt(params)

    print(f"Prompt: {formatted_prompt}")

    input = {
        "top_p": params.get("top_p", 0.9),
        "prompt": formatted_prompt,
        "max_new_tokens": params.get("max_new_tokens", 100),
        "temperature": params.get("temperature", 0.7),
        "prompt_template": "{prompt}",  # I am formatting the prompt
        "system_prompt": ""  # this is included in the prompt
    }

    try:
        prediction = replicate.models.predictions.create(
            model,
            input=input,
            stream=True,
        )
    except ReplicateError as e:
        if e.status == 401:
            raise HTTPException(status_code=401, detail="You did not pass a valid authentication token")

    return JSONResponse({
        'url': prediction.urls['stream']
    })


@router.post("/generate_completion_stream")
async def generate_completion(request: Request, token: str = Depends(get_token)):
    params = await request.json()
    replicate = Client(api_token=token)
    model = params['model_identifier']

    print(f"Prompt: {params['prompt']}")

    input = {
        "top_p": params.get("top_p", 0.9),
        "prompt": params['prompt'],
        "max_new_tokens": params.get("max_new_tokens", 100),
        "temperature": params.get("temperature", 0.7),
        "prompt_template": "{prompt}",
        # "system_prompt": params['system_prompt']
    }

    try:
        prediction = replicate.models.predictions.create(
            model,
            input=input,
            stream=True,
        )
    except ReplicateError as e:
        if e.status == 401:
            raise HTTPException(status_code=401, detail="You did not pass a valid authentication token")

    return JSONResponse({
        'url': prediction.urls['stream']
    })


def get_app() -> FastAPI:
    fast_app = FastAPI(
        title="Replicate.ai Client",
        version="0.0.1",
        openapi_url="/api/openapi.json",
    )
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_app.include_router(router, prefix="/api")
    return fast_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    fast_app = get_app()
    uvicorn.run(fast_app, host='0.0.0.0', port=args.port, log_level="info")
