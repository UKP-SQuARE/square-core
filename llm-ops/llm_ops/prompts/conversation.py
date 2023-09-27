"""
Inspiration from Fastchat conversation module
Consists of conversation prompts for models

Templates for new models will be added here
"""


import dataclasses
from typing import Optional, List, Union, Dict
from enum import auto, IntEnum


class SeparatorStyle(IntEnum):
    """Separator styles."""
    LLAMA2 = auto()
    VICUNA = auto()
    DOLLY = auto()


@dataclasses.dataclass
class Conversation:
    """A class that manages prompt templates and keeps all conversation history."""

    # The name of this template
    name: str
    # The template of the system prompt
    system_template: str = "{system_message}"
    # The system message
    system_message: str = ""
    # The names of two roles
    roles: List[str] = (("USER", "ASSISTANT"),)
    # All messages. Each item is (role, message).
    messages: List[List[str]] = ()
    # The number of few shot examples
    offset: int = 0
    # The separator style and configurations
    sep_style: SeparatorStyle = SeparatorStyle.LLAMA2
    sep: str = "\n"
    sep2: str = None
    # Stop criteria (the default one is EOS token)
    stop_str: Union[str, List[str]] = None
    # Stops generation if meeting any token in this list
    stop_token_ids: List[int] = None

    def get_prompt(self) -> str:
        """Get the prompt for generation."""
        system_prompt = self.system_template.format(system_message=self.system_message)
        if self.sep_style == SeparatorStyle.LLAMA2:
            seps = [self.sep, self.sep2]
            if self.system_message:
                ret = system_prompt
            else:
                ret = "[INST] "
            for i, (role, message) in enumerate(self.messages):
                if message:
                    if i == 0:
                        ret += message + " "
                    else:
                        ret += role + " " + message + seps[i % 2]
                else:
                    ret += role
            return ret
        elif self.sep_style == SeparatorStyle.VICUNA:
            seps = [self.sep, self.sep2]
            ret = system_prompt + seps[0]
            for i, (role, message) in enumerate(self.messages):
                if message:
                    ret += role + ": " + message + seps[i % 2]
                else:
                    ret += role + ":"
            return ret
        elif self.sep_style == SeparatorStyle.DOLLY:
            seps = [self.sep, self.sep2]
            ret = system_prompt
            for i, (role, message) in enumerate(self.messages):
                if message:
                    ret += role + ":\n" + message + seps[i % 2]
                    if i % 2 == 1:
                        ret += "\n\n"
                else:
                    ret += role + ":\n"
            return ret


    def set_system_message(self, system_message: str):
        """Set the system message."""
        self.system_message = system_message

    def append_message(self, role: str, message: str):
        """Append a new message."""
        self.messages.append([role, message])

    def update_last_message(self, message: str):
        """Update the last output.

        The last message is typically set to be None when constructing the prompt,
        so we need to update it in-place after getting the response from a model.
        """
        self.messages[-1][1] = message

    def to_gradio_chatbot(self):
        """Convert the conversation to gradio chatbot format."""
        ret = []
        for i, (role, msg) in enumerate(self.messages[self.offset :]):
            if i % 2 == 0:
                ret.append([msg, None])
            else:
                ret[-1][-1] = msg
        return ret

    def to_openai_api_messages(self):
        """Convert the conversation to OpenAI chat completion format."""
        ret = [{"role": "system", "content": self.system_message}]

        for i, (_, msg) in enumerate(self.messages[self.offset :]):
            if i % 2 == 0:
                ret.append({"role": "user", "content": msg})
            else:
                if msg is not None:
                    ret.append({"role": "assistant", "content": msg})
        return ret

    def copy(self):
        return Conversation(
            name=self.name,
            system_template=self.system_template,
            system_message=self.system_message,
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            offset=self.offset,
            sep_style=self.sep_style,
            sep=self.sep,
            sep2=self.sep2,
            stop_str=self.stop_str,
            stop_token_ids=self.stop_token_ids,
        )

    def dict(self):
        return {
            "template_name": self.name,
            "system_message": self.system_message,
            "roles": self.roles,
            "messages": self.messages,
            "offset": self.offset,
        }

# A global registry for all conversation templates
conv_templates: Dict[str, Conversation] = {}

def register_conv_template(template: Conversation, override: bool = False):
    """Register a new conversation template."""
    if not override:
        assert (
            template.name not in conv_templates
        ), f"{template.name} has been registered."

    conv_templates[template.name] = template


def get_conv_template(name: str) -> Conversation:
    """Get a conversation template."""
    return conv_templates[name].copy()


# llama2 template
# reference: https://huggingface.co/blog/codellama#conversational-instructions
# reference: https://github.com/facebookresearch/llama/blob/1a240688810f8036049e8da36b073f63d2ac552c/llama/generation.py#L212
register_conv_template(
    Conversation(
        name="llama-2",
        system_template="[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n",
        roles=("[INST]", "[/INST]"),
        sep_style=SeparatorStyle.LLAMA2,
        sep=" ",
        sep2=" </s><s>",
    )
)

# Vicuna v1.1 template
register_conv_template(
    Conversation(
        name="vicuna_v1.1",
        system_message="A chat between a curious user and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions.",
        roles=("USER", "ASSISTANT"),
        sep_style=SeparatorStyle.VICUNA,
        sep=" ",
        sep2="</s>",
    )
)

# Dolly V2 default template
register_conv_template(
    Conversation(
        name="dolly_v2",
        system_message="Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n",
        roles=("### Instruction", "### Response"),
        sep_style=SeparatorStyle.DOLLY,
        sep="\n\n",
        sep2="### End",
    )
)


# print(conv_templates)

if __name__ == "__main__":

    print("Llama-2 template:")
    conv = get_conv_template("llama-2")
    conv.set_system_message("You are a helpful, respectful and honest assistant.")
    conv.append_message(conv.roles[0], "Hello!")
    conv.append_message(conv.roles[1], "Hi!")
    conv.append_message(conv.roles[0], "How are you?")
    conv.append_message(conv.roles[1], None)
    print(conv.get_prompt())


    # Llama - 2 template:
    # --------------------------------------------------------
    # [INST] <<SYS>>
    # You are a helpful, respectful and honest assistant.
    # <</SYS>>
    # Hello! [/INST] Hi! </s><s> [INST] How are you? [/INST]
