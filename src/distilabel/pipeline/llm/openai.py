# Copyright 2023-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Optional, Union

from openai import OpenAI
from pydantic import PrivateAttr, SecretStr, field_validator

from distilabel.pipeline.llm.base import LLM
from distilabel.pipeline.step.task.types import ChatType


# TODO: OpenAI client can be used for AnyScale, TGI, vLLM, etc.
# https://github.com/vllm-project/vllm/blob/main/examples/openai_chatcompletion_client.py
class OpenAILLM(LLM):
    model: str = "gpt-3.5-turbo"
    api_key: Optional[SecretStr] = os.getenv("OPENAI_API_KEY")  # type: ignore

    _client: Optional["OpenAI"] = PrivateAttr(...)

    @field_validator("api_key")
    @classmethod
    def api_key_must_not_be_none(cls, v: Union[SecretStr, None]) -> SecretStr:
        if v is None:
            raise ValueError("You must provide an API key to use OpenAI.")
        return v

    def load(self) -> None:
        self._client = OpenAI(api_key=self.api_key.get_secret_value(), max_retries=6)  # type: ignore

    def format_input(self, input: ChatType) -> ChatType:
        return input

    def generate(
        self,
        input: ChatType,
        max_new_tokens: int = 128,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        temperature: float = 1.0,
        top_p: float = 1.0,
    ) -> str:
        chat_completions = self._client.chat.completions.create(  # type: ignore
            messages=input,  # type: ignore
            model=self.model,
            max_tokens=max_new_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            temperature=temperature,
            top_p=top_p,
            timeout=50,
        )
        return chat_completions.choices[0].message.content  # type: ignore