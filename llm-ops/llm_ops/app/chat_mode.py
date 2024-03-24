import asyncio
import aiohttp

import os
import json
import time
from typing import Optional
import torch

from llm_ops.llms.inference import ChatIO
from llm_ops.prompts.conversation import get_conv_template, SeparatorStyle
from llm_ops.llms.base_model import (
    load_model,
    get_conversation_template,
    get_generate_stream_function,
)
from llm_ops.app.chat_cli import SimpleChatIO


async def get_response(payload):
    async with aiohttp.ClientSession() as session:
        url = "https://localhost:8443/api/llm/worker_generate"
        # payload = {"prompt": "Hi", "max_new_tokens": 50}
        async with session.post(url=url, json=payload, verify_ssl=False) as resp:
            response = await resp.json()
            return response


# asyncio.run(get_response())


def chat_loop(
    model_path: str,
    conv_template: Optional[str],
    conv_system_msg: Optional[str],
    temperature: float,
    repetition_penalty: float,
    max_new_tokens: int,
    chatio: ChatIO,
    history: bool = True,
):
    # generate_stream_func = get_generate_stream_function(model, model_path)

    # model_type = str(type(model)).lower()
    # is_t5 = "t5" in model_type
    # is_codet5p = "codet5p" in model_type
    #
    # # Hardcode T5's default repetition penalty to be 1.2
    # if is_t5 and repetition_penalty == 1.0:
    #     repetition_penalty = 1.2

    # Set context length
    context_len = 2048

    # Chat
    def new_chat():
        if conv_template:
            conv = get_conv_template(conv_template)
        else:
            conv = get_conversation_template(model_path)
            print(conv)
        if conv_system_msg is not None:
            conv.set_system_message(conv_system_msg)
        return conv

    def reload_conv(conv):
        """
        Reprints the conversation from the start.
        """
        for message in conv.messages[conv.offset :]:
            chatio.prompt_for_output(message[0])
            chatio.print_output(message[1])

    conv = None

    while True:
        if not history or not conv:
            conv = new_chat()
            print("here")
            print(conv)

        try:
            print(conv.roles[0])
            inp = chatio.prompt_for_input(conv.roles[0])
        except EOFError:
            inp = ""

        if inp == "!!exit" or not inp:
            print("exit...")
            break
        elif inp == "!!reset":
            print("resetting...")
            conv = new_chat()
            continue
        elif inp == "!!remove":
            print("removing last message...")
            if len(conv.messages) > conv.offset:
                # Assistant
                if conv.messages[-1][0] == conv.roles[1]:
                    conv.messages.pop()
                # User
                if conv.messages[-1][0] == conv.roles[0]:
                    conv.messages.pop()
                reload_conv(conv)
            else:
                print("No messages to remove.")
            continue
        elif inp == "!!regen":
            print("regenerating last message...")
            if len(conv.messages) > conv.offset:
                # Assistant
                if conv.messages[-1][0] == conv.roles[1]:
                    conv.messages.pop()
                # User
                if conv.messages[-1][0] == conv.roles[0]:
                    reload_conv(conv)
                    # Set inp to previous message
                    inp = conv.messages.pop()[1]
                else:
                    # Shouldn't happen in normal circumstances
                    print("No user message to regenerate from.")
                    continue
            else:
                print("No messages to regenerate.")
                continue
        elif inp.startswith("!!save"):
            args = inp.split(" ", 1)

            if len(args) != 2:
                print("usage: !!save <filename>")
                continue
            else:
                filename = args[1]

            # Add .json if extension not present
            if not "." in filename:
                filename += ".json"

            print("saving...", filename)
            with open(filename, "w") as outfile:
                json.dump(conv.dict(), outfile)
            continue
        elif inp.startswith("!!load"):
            args = inp.split(" ", 1)

            if len(args) != 2:
                print("usage: !!load <filename>")
                continue
            else:
                filename = args[1]

            # Check if file exists and add .json if needed
            if not os.path.exists(filename):
                if (not filename.endswith(".json")) and os.path.exists(
                    filename + ".json"
                ):
                    filename += ".json"
                else:
                    print("file not found:", filename)
                    continue

            print("loading...", filename)
            with open(filename, "r") as infile:
                new_conv = json.load(infile)

            conv = get_conv_template(new_conv["template_name"])
            conv.set_system_message(new_conv["system_message"])
            conv.messages = new_conv["messages"]
            reload_conv(conv)
            continue

        conv.append_message(conv.roles[0], inp)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        # if is_codet5p:  # codet5p is a code completion model.
        #     prompt = inp

        gen_params = {
            # "model": model_path,
            "prompt": prompt,
            "temperature": temperature,
            "repetition_penalty": repetition_penalty,
            "max_new_tokens": max_new_tokens,
            "stop": conv.stop_str,
            "stop_token_ids": conv.stop_token_ids,
            "echo": False,
        }

        try:
            chatio.prompt_for_output(conv.roles[1])
            # output_stream = generate_stream_func(
            #     model,
            #     tokenizer,
            #     gen_params,
            #     device,
            #     context_len=context_len,
            #     judge_sent_end=judge_sent_end,
            # )
            output_stream = asyncio.run(get_response(gen_params))  #["text"]
            print(output_stream)
            t = time.time()
            outputs = chatio.stream_output([output_stream])
            # outputs = output_stream["text"]
            # print(outputs)
            duration = time.time() - t
            conv.update_last_message(outputs.strip())

            # if debug:
            #     num_tokens = len(tokenizer.encode(outputs))
            #     msg = {
            #         "conv_template": conv.name,
            #         "prompt": prompt,
            #         "outputs": outputs,
            #         "speed (token/s)": round(num_tokens / duration, 2),
            #     }
            #     print(f"\n{msg}\n")

        except KeyboardInterrupt:
            print("stopped generation.")
            # If generation didn't finish
            if conv.messages[-1][1] is None:
                conv.messages.pop()
                # Remove last user message, so there isn't a double up
                if conv.messages[-1][0] == conv.roles[0]:
                    conv.messages.pop()

                reload_conv(conv)


if __name__ == '__main__':
    chat_loop(
        model_path="Mistral-7B-Instruct-v0.1",
        temperature=0.7,
        repetition_penalty=1.0,
        max_new_tokens=50,
        conv_system_msg="",
        conv_template="",
        chatio=SimpleChatIO(True)
    )