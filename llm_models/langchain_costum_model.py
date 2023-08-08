import asyncio
import openai

from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

OPENAI_API_KEY=""
openai.api_key = OPENAI_API_KEY

async def open_ai_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
              {"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": "Who won the world series in 2020?"},
              {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
              {"role": "user", "content": prompt}
          ]
    )
    return response.choices[0].message.content


class CustomLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(open_ai_completion("this is a test"))
        return result

    # @property
    # def _identifying_params(self) -> Mapping[str, Any]:
    #     """Get the identifying parameters."""
    #     return {"n": self.n}

llm = CustomLLM()
print(llm("this is a test"))
