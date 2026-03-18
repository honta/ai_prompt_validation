# ai_library/llm_client.py
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from openai import OpenAI

from ai_library.config import Config


class LLMClient:
    PROMPT_INJECTION_REFINER_MODEL = "gpt-5"

    def __init__(self, api_key=None, model=None, temperature=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.temperature = Config.TEMPERATURE if temperature is None else temperature

        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=self.api_key)

    def ask(self, prompt: str) -> str:
        return self.ask_messages([{"role": "user", "content": prompt}])

    def ask_messages(
        self,
        messages: Sequence[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model or self.model,
            temperature=self.temperature if temperature is None else temperature,
            messages=list(messages),
        )
        return (response.choices[0].message.content or "").strip()

    def refine_prompt_for_injection(
        self,
        original_prompt: str,
        attempts: Sequence[dict[str, str | bool | int]],
    ) -> str:
        templates = self._load_prompt_templates()
        refiner_templates = templates["prompt_injection"]["refiner"]
        history = self._format_attempt_history(attempts)
        messages = [
            {
                "role": "system",
                "content": refiner_templates["system"],
            },
            {
                "role": "user",
                "content": refiner_templates["user"].format(
                    original_prompt=original_prompt,
                    history=history,
                ),
            },
        ]
        refined_prompt = self.ask_messages(
            messages,
            model=self.PROMPT_INJECTION_REFINER_MODEL,
        )
        return refined_prompt or original_prompt

    @staticmethod
    def _format_attempt_history(attempts: Sequence[dict[str, str | bool | int]]) -> str:
        prior_attempts = []
        for attempt in attempts:
            prior_attempts.append(
                "\n".join(
                    [
                        f"Iteration {attempt['iteration']}",
                        f"Prompt: {attempt['prompt']}",
                        f"Response: {attempt['response']}",
                        f"Resisted: {attempt['resisted']}",
                    ]
                )
            )
        return "\n\n".join(prior_attempts) if prior_attempts else "No prior attempts."

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_prompt_templates() -> dict:
        templates_path = Path(__file__).resolve().parent / "prompts" / "prompt_templates.json"
        with templates_path.open(encoding="utf-8") as templates_file:
            return json.load(templates_file)
