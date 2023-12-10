import argparse
import asyncio
import json
from typing import List

from fastapi import FastAPI, Request, BackgroundTasks, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from transformers import (
    XLNetLMHeadModel,
    XLNetTokenizer,
)
import torch
import numpy as np

router = APIRouter(tags=["prediction"])
tokenizer = None
model = None
GENERATION_VOCABULARY_MASK = None
PADDING_TEXT = """In 1991, the remains of Russian Tsar Nicholas II and his family
(except for Alexei and Maria) are discovered.
The voice of Nicholas's young son, Tsarevich Alexei Nikolaevich, narrates the
remainder of the story. 1883 Western Siberia,
a young Grigori Rasputin is asked by his father and a group of men to perform magic.
Rasputin has a vision and denounces one of the men as a horse thief. Although his
father initially slaps him for making such an accusation, Rasputin watches as the
man is chased outside and beaten. Twenty years later, Rasputin sees a vision of
the Virgin Mary, prompting him to become a priest. Rasputin quickly becomes famous,
with people, even a bishop, begging for his blessing. <eod> </s> <eos> """


def prepare_xlnet_input(args, _, tokenizer, prompt_text):
    prompt_text = (args.padding_text if args.padding_text else PADDING_TEXT) + prompt_text
    return prompt_text


@router.get("/test")
async def api_test():
    return JSONResponse({"test": "test"})


@router.post("/generate_alternatives")
async def api_generate_stream(request: Request):
    params = await request.json()
    original_text = params["text"]

    print(original_text)

    prompt_text = original_text + " </s>"

    LENGTH_OF_INITIAL_PART = tokenizer.encode(PADDING_TEXT, add_special_tokens=False, return_tensors="pt").shape[1]
    preprocessed_prompt_text = prepare_xlnet_input(args, model, tokenizer, prompt_text)
    encoded_prompt = tokenizer.encode(preprocessed_prompt_text, add_special_tokens=False, return_tensors="pt")
    encoded_prompt = encoded_prompt.to(args.device)

    print([tokenizer.convert_ids_to_tokens(int(x)) for x in encoded_prompt[0][LENGTH_OF_INITIAL_PART:]])

    encoded = [int(x) for x in list(encoded_prompt[0])]
    i = LENGTH_OF_INITIAL_PART

    sentLength = len(encoded) - LENGTH_OF_INITIAL_PART

    import torch.nn.functional as F
    assert tokenizer.convert_ids_to_tokens(6) == "<mask>"
    import collections

    queue = collections.deque()

    SAMPLES = 1

    tokenizedStrings = [tokenizer.convert_ids_to_tokens(int(x)) for x in encoded[LENGTH_OF_INITIAL_PART:]]

    subsets = set()
    # subsets of size 1
    for i in range(sentLength):
        subsets.add(("0" * i) + "1" + ("0" * (sentLength - i - 1)))

    spanLength = int(sentLength / 7) + 1
    # spans of length sentLength/7
    for subset in range(1, 2**7 - 1):
        subset_ = format(subset, "b")
        subset_ = ("0" * (7 - len(subset_))) + subset_
        assert len(subset_) == 7, subset_
        subset__ = "".join([x * spanLength for x in subset_])
        subset__ = subset__[:sentLength]
        assert len(subset__) == sentLength
        subsets.add(subset__)

    subsets_ = set()
    for subset in subsets:
        subset = list(subset)
        lastStart = 0
        subset[-1] = "0"
        for i in range(1, len(subset) - 1):
            if tokenizedStrings[i].startswith("▁"):
                lastStart = i
            if subset[i] == "1":
                if subset[i - 1] == "0":
                    if not tokenizedStrings[i].startswith("▁"):
                        for j in range(lastStart, i):
                            subset[j] = "1"
                if i + 2 < len(subset) and subset[i + 1] == "0":
                    if not tokenizedStrings[i + 1].startswith("▁"):
                        for j in range(lastStart, i + 1):
                            subset[j] = "0"
        assert len(subset) == sentLength, (len(subset), sentLength)
        subsets_.add("".join(subset))

    subsets = subsets_
    subsets_ = set()
    for subset in subsets:
        subset = list(subset)
        subset[-1] = "0"
        if "1" not in subset:
            continue
        subsets_.add("".join(subset))
    subsets = subsets_

    for subset_ in subsets:
        if "1" not in subset_:
            continue
        encoded_ = torch.LongTensor(encoded).view(1, -1).to(args.device)
        for i in range(sentLength):
            if subset_[i] == "1":
                encoded_[0, i + LENGTH_OF_INITIAL_PART] = 6
        for sample_ in range(SAMPLES):
            assert "1" in subset_

            queue.append({"free": list(subset_), "subset": subset_, "encoded": encoded_.clone(), "sample_id": sample_})

    finished = []
    perm_masks = []
    target_mappings = []
    input_idss = []
    points = []
    unprocessed_results = []

    BATCH_SIZE = 256

    while len(queue) > 0:
        point = queue.popleft()
        input_ids = point["encoded"]
        subset__ = point["free"]
        assert "1" in subset__
        if True:
            firstMask = subset__.index("1") + LENGTH_OF_INITIAL_PART
            perm_mask = torch.zeros((1, input_ids.shape[1], input_ids.shape[1]), dtype=torch.float).to(args.device)
            for i in range(len(subset__)):
                if subset__[i] == "1":
                    # Previous tokens don't see last token
                    perm_mask[:, :, i + LENGTH_OF_INITIAL_PART] = 1.0
            perm_masks.append(perm_mask)
            target_mapping = torch.zeros((1, 1, input_ids.shape[1]), dtype=torch.float).to(args.device)  # Shape [1, 1, seq_length] => let's predict one token
            target_mapping[0, 0, firstMask] = 1.0
            target_mappings.append(target_mapping)
            input_idss.append(input_ids)
            points.append(point)
            assert len(points) == (len(perm_masks))
            if len(points) == BATCH_SIZE or len(queue) == 0:
                perm_mask = torch.cat(perm_masks, dim=0)
                input_ids = torch.cat(input_idss, dim=0)
                target_mapping = torch.cat(target_mappings, dim=0)

                with torch.no_grad():
                    outputs = model(
                        input_ids, perm_mask=perm_mask, target_mapping=target_mapping)
                    # Output has shape [target_mapping.size(0), target_mapping.size(1), config.vocab_size]
                    next_token_logits = outputs[0]

                    probs = F.softmax(next_token_logits + GENERATION_VOCABULARY_MASK, dim=-1).squeeze(1)
                    next_token = torch.multinomial(probs, num_samples=1).squeeze(1)
                    for batch in range(len(points)):
                        firstMask = points[batch]["free"].index("1") + LENGTH_OF_INITIAL_PART
                        points[batch]["encoded"][0, firstMask] = int(next_token[batch])
                        points[batch]["free"][firstMask - LENGTH_OF_INITIAL_PART] = "0"
                        if "1" in points[batch]["free"]:
                            queue.append(points[batch])
                            assert "1" in points[batch]["free"]
                        else:
                            finished.append(points[batch])
                            result_tokens = [tokenizer.convert_ids_to_tokens(int(x)) for x in points[batch]["encoded"][0][LENGTH_OF_INITIAL_PART:]]
                            unprocessed_results.append(result_tokens)
                perm_masks = []
                target_mappings = []
                input_idss = []
                points = []

    processed_results = []

    for result in unprocessed_results:
        result = [x for x in result if x != "</s>"]
        words = []
        idx = 0
        for token in result:
            if token.startswith('▁'):
                words.append(token.strip('▁'))
                idx += 1
            elif idx != 0:
                words[idx - 1] += token

        processed_results.append(" ".join(words))

    return JSONResponse({"alternatives": processed_results})


def get_app() -> FastAPI:
    fast_app = FastAPI(
        title="SQuARE Sensitivity API",
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
    fast_app.include_router(router, prefix='/api')
    return fast_app


def set_seed(args):
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--padding_text", type=str, default="", help="Padding text for Transfo-XL and XLNet.")
    parser.add_argument("--seed", type=int, default=42, help="random seed for initialization")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
    parser.add_argument("--cache_dir", type=str, default="/root/.cache/huggingface")

    args = parser.parse_args()
    args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
    args.n_gpu = 0 if args.no_cuda else torch.cuda.device_count()
    set_seed(args)

    try:
        model_class = XLNetLMHeadModel
        tokenizer_class = XLNetTokenizer
    except KeyError:
        raise KeyError("the model {} you specified is not supported. You are welcome to add it and open a PR :)")

    tokenizer = tokenizer_class.from_pretrained('xlnet-large-cased', cache_dir=args.cache_dir)
    model = model_class.from_pretrained('xlnet-large-cased', cache_dir=args.cache_dir)
    model.to(args.device)
    GENERATION_VOCABULARY_MASK = torch.cuda.FloatTensor(
        [float("-inf") if ("<" in tokenizer.convert_ids_to_tokens(x)) else 0 for x in range(32000)]
    ).view(1, 1, -1)

    fast_app = get_app()
    uvicorn.run(fast_app, host='0.0.0.0', port=8000, log_level="info")
