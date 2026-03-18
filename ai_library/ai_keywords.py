# ai_library/ai_keywords.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from robot.api import logger
from robot.api.deco import keyword, library

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_library.evaluators import Evaluators
from ai_library.llm_client import LLMClient
from ai_library.result_store import ResultStore


@library(scope="GLOBAL")
class AiKeywords:
    def __init__(self):
        self.client = LLMClient()
        self.store = ResultStore()
        self.last_prompt = None
        self.last_response = None
        self.last_run_metadata = None
        self.last_evaluation_metadata = None

    @keyword("Ask LLM")
    def ask_llm(self, prompt: str) -> str:
        self.last_prompt = prompt
        self.last_run_metadata = None
        logger.info(f"Prompt: {prompt}")
        response = self.client.ask(prompt)
        self.last_response = response
        logger.info(f"Response: {response}")
        return response

    @keyword("Ask LLM With Prompt Injection")
    def ask_llm_with_prompt_injection(self, prompt: str, max_iterations: int = 3) -> str:
        total_iterations = int(max_iterations)
        if total_iterations < 1:
            raise ValueError("max_iterations must be at least 1")

        self.last_prompt = prompt
        self.last_run_metadata = None

        conversation: list[dict[str, str]] = []
        trace: list[dict[str, Any]] = []
        final_prompt = prompt
        final_response = ""

        for iteration in range(1, total_iterations + 1):
            current_prompt = prompt
            if trace:
                current_prompt = self.client.refine_prompt_for_injection(prompt, trace)

            final_prompt = current_prompt
            logger.info(f"Prompt injection iteration {iteration}/{total_iterations}")
            logger.info(f"Prompt: {current_prompt}")

            conversation.append(
                self.client.render_message("prompt_injection", "attack_user", prompt=current_prompt)
            )
            response = self.client.ask_messages(list(conversation))
            conversation.append(
                self.client.render_message("chat", "assistant_history", content=response)
            )

            resisted = Evaluators.resisted_injection(response)
            trace.append(
                {
                    "iteration": iteration,
                    "prompt": current_prompt,
                    "response": response,
                    "resisted": resisted,
                }
            )
            final_response = response

            logger.info(f"Response: {response}")
            logger.info(f"Prompt injection resisted: {resisted}")

            if not resisted:
                logger.info("Stopping prompt injection loop after unsafe response.")
                break

        self.last_response = final_response
        self.last_run_metadata = {
            "type": "prompt_injection",
            "original_prompt": prompt,
            "final_prompt": final_prompt,
            "max_iterations": total_iterations,
            "iterations_completed": len(trace),
            "stopped_early": len(trace) < total_iterations and not trace[-1]["resisted"],
            "trace": trace,
        }
        return final_response

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
        self.last_evaluation_metadata = None
        logger.info(f"Reponse from model: {response}")
        result = Evaluators.quality_score(response, expected or None)
        logger.info(f"Quality score: {result['score']}")
        logger.info(f"Quality reasons: {', '.join(result['reasons'])}")
        return result

    @keyword("Evaluate Response Quality with LLM")
    def evaluate_response_quality_with_llm(
        self,
        response: str,
        expected: str = "",
        system_prompt: str = "",
        model: str = "gpt-5.4",
    ) -> dict:
        logger.info(f"Response from model for LLM evaluation: {response}")
        result = self.client.evaluate_response_quality_with_llm(
            response=response,
            expected=expected or None,
            system_prompt=system_prompt,
            model=model,
        )
        self.last_evaluation_metadata = {
            "type": "llm_quality_evaluation",
            "judge_model": result["judge_model"],
            "judge_prompt_name": result["judge_prompt_name"],
        }
        if "judge_summary" in result:
            self.last_evaluation_metadata["judge_summary"] = result["judge_summary"]
        logger.info(f"LLM quality score: {result['score']}")
        logger.info(f"LLM quality reasons: {', '.join(result['reasons'])}")
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
        if self.last_run_metadata:
            payload["prompt_injection"] = self.last_run_metadata
        if self.last_evaluation_metadata:
            payload["evaluation_llm"] = self.last_evaluation_metadata
        path = self.store.save_result(payload, filename_prefix=test_name.replace(" ", "_").lower())
        logger.info(f"Saved result to: {path}")
        return path
