# ai_library/llm_client.py
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from openai import OpenAI

from ai_library.config import Config


class LLMClient:
    PROMPT_INJECTION_REFINER_MODEL = "gpt-5.4"
    QUALITY_EVALUATION_MODEL = "gpt-5.4"

    def __init__(self, api_key=None, model=None, temperature=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.temperature = Config.TEMPERATURE if temperature is None else temperature

        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=self.api_key)

    def ask(self, prompt: str) -> str:
        return self.ask_messages([self.render_message("chat", "default_user", prompt=prompt)])

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
        history = self._format_attempt_history(attempts)
        messages = [
            self.render_message("prompt_injection", "refiner_system"),
            self.render_message(
                "prompt_injection",
                "refiner_user",
                original_prompt=original_prompt,
                history=history,
            ),
        ]
        refined_prompt = self.ask_messages(
            messages,
            model=self.PROMPT_INJECTION_REFINER_MODEL,
        )
        return refined_prompt or original_prompt

    def render_message(self, group: str, name: str, **kwargs: str | int | bool) -> dict[str, str]:
        template = self.get_template_value(group, name)
        return {
            "role": template["role"],
            "content": template["content"].format(**kwargs),
        }

    def render_text(self, group: str, name: str, **kwargs: str | int | bool) -> str:
        template = self.get_template_value(group, name)
        if not isinstance(template, str):
            raise TypeError(f"Template '{group}.{name}' is not a text template")
        return template.format(**kwargs)

    def get_template_value(self, *path: str) -> dict | str:
        value: dict | str = self._load_prompt_templates()
        for key in path:
            if not isinstance(value, dict) or key not in value:
                joined_path = ".".join(path)
                raise KeyError(f"Template path not found: {joined_path}")
            value = value[key]
        return value

    def evaluate_response_quality_with_llm(
        self,
        response: str,
        expected: str | None = None,
        system_prompt: str = "",
        model: str | None = None,
    ) -> dict:
        effective_model = model or self.QUALITY_EVALUATION_MODEL
        expected_section = (
            self.render_text("quality_evaluation", "expected_present", expected=expected)
            if expected
            else self.render_text("quality_evaluation", "expected_missing")
        )
        messages = [
            (
                {
                    "role": "system",
                    "content": system_prompt.strip(),
                }
                if system_prompt.strip()
                else self.render_message("quality_evaluation", "judge_system_default")
            ),
            self.render_message(
                "quality_evaluation",
                "judge_user",
                response=response,
                expected_section=expected_section,
            ),
        ]
        raw_result = self.ask_messages(messages, model=effective_model)
        return self._parse_quality_evaluation_result(
            raw_result,
            model=effective_model,
            prompt_name=(
                "custom_system_prompt"
                if system_prompt.strip()
                else "quality_evaluation.judge_system_default"
            ),
        )

    @staticmethod
    def _format_attempt_history(attempts: Sequence[dict[str, str | bool | int]]) -> str:
        templates = LLMClient._load_prompt_templates()["prompt_injection"]
        prior_attempts = []
        for attempt in attempts:
            prior_attempts.append(
                templates["history_entry"].format(
                    iteration=attempt["iteration"],
                    prompt=attempt["prompt"],
                    response=attempt["response"],
                    resisted=attempt["resisted"],
                )
            )
        return "\n\n".join(prior_attempts) if prior_attempts else templates["history_empty"]

    @staticmethod
    def _parse_quality_evaluation_result(
        raw_result: str,
        model: str,
        prompt_name: str,
    ) -> dict:
        try:
            parsed = json.loads(raw_result)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM quality evaluator returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise ValueError("LLM quality evaluator must return a JSON object")
        if "score" not in parsed or "reasons" not in parsed:
            raise ValueError("LLM quality evaluator JSON must contain 'score' and 'reasons'")

        try:
            score = float(parsed["score"])
        except (TypeError, ValueError) as exc:
            raise ValueError("LLM quality evaluator score must be numeric") from exc

        if not 0.0 <= score <= 1.0:
            raise ValueError("LLM quality evaluator score must be between 0.0 and 1.0")

        reasons = parsed["reasons"]
        if not isinstance(reasons, list) or not all(isinstance(reason, str) for reason in reasons):
            raise ValueError("LLM quality evaluator reasons must be a list of strings")
        if not reasons:
            raise ValueError("LLM quality evaluator reasons must not be empty")

        result = {
            "score": round(score, 2),
            "reasons": reasons,
            "judge_model": model,
            "judge_type": "llm",
            "judge_prompt_name": prompt_name,
        }
        if isinstance(parsed.get("summary"), str) and parsed["summary"].strip():
            result["judge_summary"] = parsed["summary"].strip()
        return result

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_prompt_templates() -> dict:
        templates_path = Path(__file__).resolve().parent / "prompts" / "prompt_templates.json"
        with templates_path.open(encoding="utf-8") as templates_file:
            return json.load(templates_file)
