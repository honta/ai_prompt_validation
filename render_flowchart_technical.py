#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


WIDTH = 2200
HEIGHT = 1500
BACKGROUND = "#f5efe7"
TEXT = "#203040"
MUTED = "#687585"
BOX_FILL = "#fcfaf6"
BOX_BORDER = "#314760"
ARROW = "#586d86"

OUTPUT_PATH = Path(__file__).with_name("ai_prompt_validation_workflow_technical.png")


@dataclass(frozen=True)
class BoxSpec:
    x: int
    y: int
    w: int
    h: int
    title: str
    accent: str
    body: list[str]

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    @property
    def center_left(self) -> tuple[int, int]:
        return (self.x, self.y + self.h // 2)

    @property
    def center_right(self) -> tuple[int, int]:
        return (self.x + self.w, self.y + self.h // 2)

    @property
    def center_top(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y)

    @property
    def center_bottom(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = load_font(34, bold=True)
SUBTITLE_FONT = load_font(17)
BOX_TITLE_FONT = load_font(22, bold=True)
BODY_FONT = load_font(15)
LABEL_FONT = load_font(13)


def draw_box(draw: ImageDraw.ImageDraw, box: BoxSpec) -> None:
    x1, y1, x2, y2 = box.rect
    draw.rounded_rectangle(box.rect, radius=20, fill=BOX_FILL, outline=BOX_BORDER, width=3)
    draw.rounded_rectangle((x1, y1, x2, y1 + 34), radius=20, fill=box.accent, outline=box.accent)
    draw.rectangle((x1, y1 + 18, x2, y1 + 34), fill=box.accent)
    draw.text((x1 + 14, y1 + 6), box.title, font=BOX_TITLE_FONT, fill="white")

    max_chars = max(28, int((box.w - 28) / 8.2))
    y = y1 + 48
    for bullet in box.body:
        lines = wrap(f"- {bullet}", width=max_chars)
        for line in lines:
            draw.text((x1 + 14, y), line, font=BODY_FONT, fill=TEXT)
            y += 21
        y += 4


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    label: str | None = None,
) -> None:
    draw.line((start, end), fill=ARROW, width=4)
    ex, ey = end
    sx, sy = start
    if abs(ex - sx) >= abs(ey - sy):
        direction = 1 if ex >= sx else -1
        head = [(ex, ey), (ex - 14 * direction, ey - 8), (ex - 14 * direction, ey + 8)]
    else:
        direction = 1 if ey >= sy else -1
        head = [(ex, ey), (ex - 8, ey - 14 * direction), (ex + 8, ey - 14 * direction)]
    draw.polygon(head, fill=ARROW)
    if label:
        lx = (sx + ex) // 2
        ly = (sy + ey) // 2 - 18
        draw.text((lx, ly), label, font=LABEL_FONT, fill=MUTED, anchor="mm")


def elbow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    via: tuple[int, int],
    end: tuple[int, int],
    label: str | None = None,
) -> None:
    draw.line((start, via), fill=ARROW, width=4)
    draw.line((via, end), fill=ARROW, width=4)
    ex, ey = end
    vx, vy = via
    if abs(ex - vx) >= abs(ey - vy):
        direction = 1 if ex >= vx else -1
        head = [(ex, ey), (ex - 14 * direction, ey - 8), (ex - 14 * direction, ey + 8)]
    else:
        direction = 1 if ey >= vy else -1
        head = [(ex, ey), (ex - 8, ey - 14 * direction), (ex + 8, ey - 14 * direction)]
    draw.polygon(head, fill=ARROW)
    if label:
        lx = (start[0] + via[0]) // 2
        ly = (start[1] + via[1]) // 2 - 18
        draw.text((lx, ly), label, font=LABEL_FONT, fill=MUTED, anchor="mm")


def build_boxes() -> dict[str, BoxSpec]:
    return {
        "robot": BoxSpec(
            40,
            110,
            470,
            255,
            "Robot Test Suites",
            "#2e63d3",
            [
                "tests/functional_tests.robot exercises factual answers, consistency, uncertainty, and LLM judging.",
                "tests/prompt_injection.robot checks single-shot and iterative prompt-injection resistance.",
                "Robot keywords are the public test API used by local runs and CI.",
            ],
        ),
        "keywords": BoxSpec(
            560,
            110,
            540,
            285,
            "AiKeywords Library",
            "#15896c",
            [
                "Ask LLM sends the user prompt through the configured OpenAI chat model.",
                "Ask LLM With Prompt Injection keeps chat history, refines later attempts, and records a trace.",
                "Evaluate Response Quality uses rule-based heuristics; Evaluate Response Quality with LLM uses a judge model.",
                "Save Evaluation Result persists response, evaluation, and optional prompt-injection or judge metadata.",
            ],
        ),
        "llm": BoxSpec(
            1150,
            110,
            500,
            285,
            "LLMClient",
            "#127c79",
            [
                "Wraps OpenAI chat completions and returns the assistant content as a stripped string.",
                "render_message() and render_text() load all OpenAI-bound prompt templates from JSON.",
                "Supports three paths: normal ask, prompt-injection refinement, and LLM-based quality evaluation.",
                "Parses strict JSON from the judge model and validates score and reasons.",
            ],
        ),
        "templates": BoxSpec(
            1700,
            110,
            460,
            285,
            "Prompt Templates JSON",
            "#8f49da",
            [
                "ai_library/prompts/prompt_templates.json stores user/system messages and text fragments.",
                "Covers default chat prompts, prompt-injection refiner prompts, and LLM-quality judge prompts.",
                "Keeping prompts outside Python makes prompt changes auditable and testable.",
            ],
        ),
        "evaluators": BoxSpec(
            40,
            485,
            470,
            250,
            "Rule-Based Evaluators",
            "#c46d0a",
            [
                "contains_expected(), consistency_score(), appears_grounded(), and resisted_injection() implement heuristic checks.",
                "quality_score() produces a simple score/reasons dict without a second model call.",
                "These checks remain compatible with threshold assertions in Robot.",
            ],
        ),
        "results": BoxSpec(
            560,
            485,
            540,
            250,
            "ResultStore + Results",
            "#36495e",
            [
                "save_result() writes timestamped JSON payloads to results/.",
                "Saved payloads may include evaluation data, prompt-injection traces, and LLM-judge metadata.",
                "These artifacts support review, debugging, and future comparison over time.",
            ],
        ),
        "tests": BoxSpec(
            1150,
            485,
            500,
            250,
            "Unit Test Harness",
            "#2e63d3",
            [
                "tests/test_ai_keywords.py mocks keyword orchestration and saved metadata.",
                "tests/test_llm_client.py validates prompt rendering, OpenAI calls, JSON parsing, and model overrides.",
                "tests/robot_stub.py allows unittest execution without installing Robot Framework in the interpreter.",
            ],
        ),
        "ci": BoxSpec(
            1700,
            485,
            460,
            250,
            "CI Workflow",
            "#127c79",
            [
                ".github/workflows/workflow.yaml installs dependencies, runs robot -d results tests/, and uploads the results artifact.",
                "OPENAI_API_KEY comes from GitHub Actions secrets and OPENAI_MODEL defaults to gpt-4o-mini in CI.",
            ],
        ),
        "openai": BoxSpec(
            280,
            860,
            620,
            280,
            "OpenAI API Interactions",
            "#8f49da",
            [
                "Primary model handles normal answers for Ask LLM using OPENAI_MODEL from config.",
                "Prompt-injection refinement uses a dedicated GPT-5.4 path to propose the next adversarial query.",
                "LLM-based quality evaluation uses a judge model, defaulting to gpt-5.4, and must return strict JSON.",
            ],
        ),
        "flow": BoxSpec(
            950,
            860,
            570,
            280,
            "End-to-End Runtime Flow",
            "#c46d0a",
            [
                "1) Robot test invokes a keyword from AiKeywords.",
                "2) The keyword calls LLMClient and, when needed, Evaluators or ResultStore.",
                "3) Prompt templates shape every OpenAI message used by refinement or judging.",
                "4) Results and traces are written to JSON files for later inspection.",
            ],
        ),
        "artifacts": BoxSpec(
            1570,
            860,
            590,
            280,
            "Generated Artifacts",
            "#15896c",
            [
                "results/*.json stores evaluation snapshots.",
                "output.xml, log.html, and report.html come from Robot runs.",
                "This technical workflow PNG documents the code path from tests to external API calls.",
            ],
        ),
    }


def render() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    draw.text((40, 24), "AI Prompt Validation - Technical Workflow", font=TITLE_FONT, fill=TEXT)
    draw.text(
        (40, 64),
        "Robot Framework entrypoints, keyword orchestration, OpenAI chat calls, prompt templates, evaluation paths, and persisted test artifacts.",
        font=SUBTITLE_FONT,
        fill=MUTED,
    )

    boxes = build_boxes()
    for box in boxes.values():
        draw_box(draw, box)

    arrow(draw, boxes["robot"].center_right, boxes["keywords"].center_left, label="invoke keywords")
    arrow(draw, boxes["keywords"].center_right, boxes["llm"].center_left, label="chat + judge requests")
    arrow(draw, boxes["llm"].center_right, boxes["templates"].center_left, label="load templates")

    arrow(draw, boxes["robot"].center_bottom, boxes["evaluators"].center_top, label="assertions")
    arrow(draw, boxes["keywords"].center_bottom, boxes["results"].center_top, label="save payload")
    arrow(draw, boxes["llm"].center_bottom, boxes["tests"].center_top, label="mocked in unittest")
    arrow(draw, boxes["templates"].center_bottom, boxes["ci"].center_top, label="used in CI runs")

    elbow(
        draw,
        boxes["llm"].center_bottom,
        (boxes["llm"].center_bottom[0], 790),
        boxes["openai"].center_top,
        label="chat.completions.create",
    )
    arrow(draw, boxes["evaluators"].center_right, boxes["flow"].center_left, label="heuristic score")
    arrow(draw, boxes["results"].center_bottom, boxes["flow"].center_top, label="persisted data")
    arrow(draw, boxes["tests"].center_bottom, boxes["flow"].center_top, label="coverage")
    arrow(draw, boxes["ci"].center_bottom, boxes["artifacts"].center_top, label="upload results")

    arrow(draw, boxes["openai"].center_right, boxes["flow"].center_left, label="assistant output")
    arrow(draw, boxes["flow"].center_right, boxes["artifacts"].center_left, label="files + reports")

    image.save(OUTPUT_PATH, format="PNG")
    print(f"Saved flowchart to {OUTPUT_PATH}")


if __name__ == "__main__":
    render()
