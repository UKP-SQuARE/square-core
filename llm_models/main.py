from fastapi import FastAPI
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from pydantic import BaseModel, confloat

app = FastAPI()

class ModelParams(BaseModel):
    text: str
    max_new_tokens: int
    temperature: confloat(ge=0, le=1)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    global tokenizer, model
    print("Loading model ...")
    tokenizer = AutoTokenizer.from_pretrained("data/Llama-2-7b-chat-hf")
    model = AutoModelForCausalLM.from_pretrained("data/Llama-2-7b-chat-hf")
    print("Model loaded")

@app.post("/fake-generate")
def fake_generate(params: ModelParams):
    print("Fake Generating ...")
    return params.text + " " + params.text

# Create a path operation function that takes the input prompt as a parameter and returns the output of the language model as a response
@app.post("/generate")
def generate(params: ModelParams):
    print("Generating ...")
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=params.max_new_tokens,
        temperature=params.temperature,
    )
    generated_text = pipe(params.text)
    return generated_text
