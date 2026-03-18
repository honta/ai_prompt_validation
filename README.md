# AI Prompt Validation

Robot Framework-based acceptance tests for LLM behavior, with reusable keywords for direct prompting, prompt-injection probing, rule-based scoring, and LLM-based quality judging.

![Technical workflow](./ai_prompt_validation_workflow_technical.png)

## What This Repo Does

- Sends prompts to an OpenAI chat model through a small Python library exposed as Robot Framework keywords.
- Verifies core QA behaviors such as factual correctness, consistency, uncertainty handling, and prompt-injection resistance.
- Supports iterative prompt-injection attempts where later attack prompts are refined with a GPT-5.4 model.
- Supports two quality-evaluation modes:
  - rule-based heuristics in Python
  - LLM-based judging that returns strict JSON with `score` and `reasons`
- Saves timestamped JSON results under `results/` for later review.

## Technical Workflow

At a high level:

1. A Robot test from [functional_tests.robot](/home/prd/other_projects/ai_prompt_validation/tests/functional_tests.robot) or [prompt_injection.robot](/home/prd/other_projects/ai_prompt_validation/tests/prompt_injection.robot) calls a keyword from [ai_keywords.py](/home/prd/other_projects/ai_prompt_validation/ai_library/ai_keywords.py).
2. `AiKeywords` delegates OpenAI requests and prompt rendering to [llm_client.py](/home/prd/other_projects/ai_prompt_validation/ai_library/llm_client.py).
3. Prompt content for refinement and judging is loaded from [prompt_templates.json](/home/prd/other_projects/ai_prompt_validation/ai_library/prompts/prompt_templates.json).
4. Heuristic checks are handled by [evaluators.py](/home/prd/other_projects/ai_prompt_validation/ai_library/evaluators.py).
5. Saved JSON artifacts are written by [result_store.py](/home/prd/other_projects/ai_prompt_validation/ai_library/result_store.py).

The generated technical diagram can be recreated with:

```bash
python3 render_flowchart_technical.py
```

This writes `ai_prompt_validation_workflow_technical.png` in the repo root.

## Project Structure

```text
ai_library/
  ai_keywords.py
  llm_client.py
  evaluators.py
  result_store.py
  config.py
  prompts/prompt_templates.json
tests/
  functional_tests.robot
  prompt_injection.robot
  test_ai_keywords.py
  test_llm_client.py
render_flowchart_technical.py
README.md
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
export OPENAI_API_KEY=your_key_here
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_TEMPERATURE=0
export RESULTS_DIR=results
```

You can also keep these values in `ai_library/.env`.

## Available Keywords

Main Robot keywords exposed by `AiKeywords`:

- `Ask LLM`
- `Ask LLM With Prompt Injection`
- `Response Should Contain`
- `Responses Should Be Consistent`
- `Response Should Show Uncertainty`
- `Response Should Resist Prompt Injection`
- `Evaluate Response Quality`
- `Evaluate Response Quality with LLM`
- `Quality Score Should Be At Least`
- `Save Evaluation Result`

### Example

```robot
*** Settings ***
Library    ai_library.ai_keywords.AiKeywords

*** Test Cases ***
Capital Of Poland Should Be Correct With LLM Judge
    ${response}=    Ask LLM    What is the capital of Poland?
    ${evaluation}=    Evaluate Response Quality With LLM    ${response}    Warsaw
    Quality Score Should Be At Least    ${evaluation}    0.60
    Save Evaluation Result    capital_of_poland_llm_judge    ${response}    ${evaluation}
```

## Running Tests

Run Robot suites:

```bash
robot -d results tests/
```

Run unit tests:

```bash
python3 -m unittest discover -s tests -v
```

## Results and Artifacts

- `results/*.json` stores saved evaluation payloads.
- `output.xml`, `log.html`, and `report.html` are standard Robot Framework outputs.
- Prompt-injection runs may add iterative trace data.
- LLM-based evaluation may add judge metadata such as model and prompt name.

## CI

GitHub Actions in [.github/workflows/workflow.yaml](/home/prd/other_projects/ai_prompt_validation/.github/workflows/workflow.yaml) runs Robot tests on push and pull request, using `OPENAI_API_KEY` from repository secrets and uploading the `results/` directory as an artifact.

## Notes

- The flowchart renderer uses Pillow (`PIL`).
- The current repository focuses on behavior validation and artifact capture; historical trend comparison is a logical next step for the results layer.
