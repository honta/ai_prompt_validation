# ai_library/ai_keywords.py
from __future__ import annotations

import sys
from pathlib import Path

from robot.api import logger
from robot.api.deco import keyword, library

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_library.evaluators import Evaluators
from ai_library.llm_client import LLMClient
from ai_library.result_store import ResultStore


@library
class AiKeywords:
    def __init__(self):
        self.client = LLMClient()
        self.store = ResultStore()
        self.last_prompt = None
        self.last_response = None

    @keyword("Ask LLM")
    def ask_llm(self, prompt: str) -> str:
        self.last_prompt = prompt
        logger.info(f"Prompt: {prompt}")
        response = self.client.ask(prompt)
        self.last_response = response
        logger.info(f"Response: {response}")
        return response

    @keyword("Response Should Contain")
    def response_should_contain(self, response: str, expected: str):
        if not Evaluators.contains_expected(response, expected):
            raise AssertionError(
                f"Expected response to contain '{expected}', but got: {response}"
            )

    @keyword("Responses Should Be Consistent")
    def responses_should_be_consistent(self, first: str, second: str, threshold: float = 0.9):
        score = Evaluators.consistency_score(first, second)
        logger.info(f"Consistency score: {score}")
        if score < float(threshold):
            raise AssertionError(
                f"Responses are not consistent enough. Score={score}, threshold={threshold}"
            )

    @keyword("Response Should Show Uncertainty")
    def response_should_show_uncertainty(self, response: str):
        if not Evaluators.appears_grounded(response):
            raise AssertionError(
                "Expected the model to acknowledge uncertainty or lack of verifiable data"
            )

    @keyword("Response Should Resist Prompt Injection")
    def response_should_resist_prompt_injection(self, response: str):
        if not Evaluators.resisted_injection(response):
            raise AssertionError(
                "Expected a refusal or safe behavior for injection-style prompt"
            )

    @keyword("Evaluate Response Quality")
    def evaluate_response_quality(self, response: str, expected: str = "") -> dict:
        result = Evaluators.quality_score(response, expected or None)
        logger.info(f"Quality score: {result['score']}")
        logger.info(f"Quality reasons: {', '.join(result['reasons'])}")
        return result

    @keyword("Quality Score Should Be At Least")
    def quality_score_should_be_at_least(self, evaluation: dict, minimum: float):
        actual = float(evaluation["score"])
        required = float(minimum)
        if actual < required:
            raise AssertionError(f"Quality score too low: {actual} < {required}")

    @keyword("Save Evaluation Result")
    def save_evaluation_result(self, test_name: str, response: str, evaluation: dict) -> str:
        payload = {
            "test_name": test_name,
            "prompt": self.last_prompt,
            "response": response,
            "evaluation": evaluation,
        }
        path = self.store.save_result(payload, filename_prefix=test_name.replace(" ", "_").lower())
        logger.info(f"Saved result to: {path}")
        return path
