"""Additional information of the models."""
from collections import namedtuple
from typing import List


ModelInfo = namedtuple("ModelInfo", ["simple_name", "link", "description"])


model_info = {}


def register_model_info(
    full_names: List[str], simple_name: str, link: str, description: str
):
    info = ModelInfo(simple_name, link, description)

    for full_name in full_names:
        model_info[full_name] = info


def get_model_info(name: str) -> ModelInfo:
    return model_info[name]


register_model_info(
    ["gpt-4"],
    "ChatGPT-4",
    "https://openai.com/research/gpt-4",
    "ChatGPT-4 by OpenAI",
)
register_model_info(
    ["gpt-3.5-turbo"],
    "ChatGPT-3.5",
    "https://openai.com/blog/chatgpt",
    "ChatGPT-3.5 by OpenAI",
)
register_model_info(
    ["claude-2"],
    "Claude",
    "https://www.anthropic.com/index/claude-2",
    "Claude 2 by Anthropic",
)
register_model_info(
    ["claude-1"],
    "Claude",
    "https://www.anthropic.com/index/introducing-claude",
    "Claude by Anthropic",
)
register_model_info(
    ["claude-instant-1"],
    "Claude Instant",
    "https://www.anthropic.com/index/introducing-claude",
    "Claude Instant by Anthropic",
)
register_model_info(
    ["palm-2"],
    "PaLM 2 Chat",
    "https://cloud.google.com/vertex-ai/docs/release-notes#May_10_2023",
    "PaLM 2 for Chat (chat-bison@001) by Google",
)
register_model_info(
    ["llama-2-70b-chat", "llama-2-34b-chat", "llama-2-13b-chat", "llama-2-7b-chat"],
    "Llama 2",
    "https://ai.meta.com/llama/",
    "open foundation and fine-tuned chat models by Meta",
)
register_model_info(
    ["mistral-7b-instruct-v0.1", "mistral-7b-v0.1"],
    "Mistral-7B",
    "https://mistral.ai/",
    "open foundation and fine-tuned chat models by Mistral AI",
)
register_model_info(
    ["codellama-34b-instruct", "codellama-13b-instruct", "codellama-7b-instruct"],
    "Code Llama",
    "https://ai.meta.com/blog/code-llama-large-language-model-coding/",
    "open foundation models for code by Meta",
)
register_model_info(
    [
        "vicuna-33b",
        "vicuna-33b-v1.3",
        "vicuna-13b",
        "vicuna-13b-v1.3",
        "vicuna-7b",
        "vicuna-7b-v1.3",
    ],
    "Vicuna",
    "https://lmsys.org/blog/2023-03-30-vicuna/",
    "a chat assistant fine-tuned from LLaMA on user-shared conversations by LMSYS",
)
register_model_info(
    ["gpt4all-13b-snoozy"],
    "GPT4All-Snoozy",
    "https://github.com/nomic-ai/gpt4all",
    "a finetuned LLaMA model on assistant style data by Nomic AI",
)
register_model_info(
    ["alpaca-13b"],
    "Alpaca",
    "https://crfm.stanford.edu/2023/03/13/alpaca.html",
    "a model fine-tuned from LLaMA on instruction-following demonstrations by Stanford",
)
register_model_info(
    ["oasst-pythia-12b"],
    "OpenAssistant (oasst)",
    "https://open-assistant.io",
    "an Open Assistant for everyone by LAION",
)
register_model_info(
    ["oasst-sft-7-llama-30b"],
    "OpenAssistant (oasst)",
    "https://open-assistant.io",
    "an Open Assistant for everyone by LAION",
)
register_model_info(
    ["llama-7b", "llama-13b"],
    "LLaMA",
    "https://arxiv.org/abs/2302.13971",
    "open and efficient foundation language models by Meta",
)
register_model_info(
    ["open-llama-7b-v2-open-instruct", "open-llama-7b-open-instruct"],
    "Open LLaMa (Open Instruct)",
    "https://medium.com/vmware-data-ml-blog/starter-llm-for-the-enterprise-instruction-tuning-openllama-7b-d05fc3bbaccc",
    "Open LLaMa fine-tuned on instruction-following data by VMware",
)
register_model_info(
    ["dolly-v2-12b"],
    "Dolly",
    "https://www.databricks.com/blog/2023/04/12/dolly-first-open-commercially-viable-instruction-tuned-llm",
    "an instruction-tuned open large language model by Databricks",
)
register_model_info(
    ["codet5p-6b"],
    "CodeT5p-6b",
    "https://huggingface.co/Salesforce/codet5p-6b",
    "Code completion model released by Salesforce",
)
register_model_info(
    ["fastchat-t5-3b", "fastchat-t5-3b-v1.0"],
    "FastChat-T5",
    "https://huggingface.co/lmsys/fastchat-t5-3b-v1.0",
    "a chat assistant fine-tuned from FLAN-T5 by LMSYS",
)
register_model_info(
    ["redpajama-incite-7b-chat"],
    "RedPajama-INCITE-7B-Chat",
    "https://huggingface.co/togethercomputer/RedPajama-INCITE-7B-Chat",
    "A chatbot fine-tuned from RedPajama-INCITE-7B-Base by Together",
)
register_model_info(
    [
        "falcon-7b",
        "falcon-7b-instruct",
        "falcon-40b",
        "falcon-40b-instruct",
        "falcon-180b",
        "falcon-180b-chat",
    ],
    "Falcon",
    "https://huggingface.co/tiiuae/falcon-180B",
    "TII's flagship series of large language models",
)
