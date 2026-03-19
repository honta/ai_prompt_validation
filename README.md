# Intro
LLM systems are non-deterministic, prone to hallucinations, and difficult to validate using traditional QA approaches.

This project provides a framework for automated validation of AI systems, including consistency testing, hallucination detection, prompt injection resistance, and LLM-based evaluation.


# AI Prompt Validation

Robot Framework-based acceptance tests for LLM behavior, with reusable keywords for direct prompting, prompt-injection probing, rule-based scoring, and LLM-based quality judging.

![Technical workflow](./ai_prompt_validation_workflow_technical.png)

## Technical Workflow

At a high level:

1. A Robot test from [functional_tests.robot](/home/prd/other_projects/ai_prompt_validation/tests/functional_tests.robot) or [prompt_injection.robot](/home/prd/other_projects/ai_prompt_validation/tests/prompt_injection.robot) calls a keyword from [ai_keywords.py](/home/prd/other_projects/ai_prompt_validation/ai_library/ai_keywords.py).
2. `AiKeywords` delegates OpenAI requests and prompt rendering to [llm_client.py](/home/prd/other_projects/ai_prompt_validation/ai_library/llm_client.py).
3. Prompt content for refinement and judging is loaded from [prompt_templates.json](/home/prd/other_projects/ai_prompt_validation/ai_library/prompts/prompt_templates.json).
4. Heuristic checks are handled by [evaluators.py](/home/prd/other_projects/ai_prompt_validation/ai_library/evaluators.py).
5. Saved JSON artifacts are written by [result_store.py](/home/prd/other_projects/ai_prompt_validation/ai_library/result_store.py).


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
  datasets/
    functional_cases.csv
    prompt_injection_cases.csv
unit_tests/
  test_ai_keywords.py
  test_llm_client.py
  robot_stub.py
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

### Example

Example data-driven suite:

```robot
*** Settings ***
Library    DataDriver    file=datasets/functional_cases.csv    encoding=utf-8    dialect=excel
Library    ai_library.ai_keywords.AiKeywords
Test Template    Run Functional Dataset Case

*** Test Cases ***
Functional Dataset Case
    ${case_type}    ${prompt}    ${prompt_second}    ${expected}    ${min_score}    ${consistency_threshold}    ${result_id}
```

Matching CSV row:

```csv
*** Test Cases ***,${case_type},${prompt},${prompt_second},${expected},${min_score},${consistency_threshold},${result_id}
"Capital of Poland should pass LLM judge","llm_judge","What is the capital of Poland?","","Warsaw","0.60","","capital_of_poland_llm_judge"
```

## Running Tests

Run Robot suites:

```bash
robot -d results tests/
```

The suites in `tests/` are data-driven:

- [tests/datasets/functional_cases.csv](/home/prd/other_projects/ai_prompt_validation/tests/datasets/functional_cases.csv) defines the functional behavior cases.
- [tests/datasets/prompt_injection_cases.csv](/home/prd/other_projects/ai_prompt_validation/tests/datasets/prompt_injection_cases.csv) defines the prompt-injection cases.
- Each CSV row becomes a separate Robot test via `DataDriver`.
- The first CSV column is `*** Test Cases ***`, followed by `${argument}` columns expected by the suite template.

Run unit tests:

```bash
python3 -m unittest discover -s unit_tests -v
```

## Results and Artifacts

- `results/*.json` stores saved evaluation payloads.
- `output.xml`, `log.html`, and `report.html` are standard Robot Framework outputs.
- Prompt-injection runs may add iterative trace data.
- LLM-based evaluation may add judge metadata such as model and prompt name.

## CI

GitHub Actions in [.github/workflows/workflow.yaml](/home/prd/other_projects/ai_prompt_validation/.github/workflows/workflow.yaml) runs Robot tests on push and pull request, using `OPENAI_API_KEY` from repository secrets and uploading the `results/` directory as an artifact.

## Example report

- [RobotFramework report file](./example_report/report.html)
- [RobotFramework log file](./example_report/log.html)

![Example report screenshot](./example_report/example_report_screenshot.png)
