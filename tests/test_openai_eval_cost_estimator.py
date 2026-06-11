from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "estimate_openai_eval_cost.py"
SPEC = importlib.util.spec_from_file_location("estimate_openai_eval_cost", SCRIPT_PATH)
assert SPEC is not None
estimator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = estimator
SPEC.loader.exec_module(estimator)


def test_estimate_tokens_from_chars_rounds_up() -> None:
    assert estimator.estimate_tokens_from_chars("a" * 9) == 3


def test_estimate_costs_uses_output_budget_and_prices(monkeypatch) -> None:
    monkeypatch.setattr(estimator, "count_tokens", lambda text, model: len(text.split()))
    monkeypatch.setattr(estimator, "render_input", lambda question: question)
    items = [
        estimator.EvalItem(question="one two three"),
        estimator.EvalItem(question="one two three four five"),
    ]

    estimates = estimator.estimate_costs(
        items=items,
        models=["custom-model"],
        visible_output_tokens=100,
        reasoning_output_tokens=50,
        input_price_override=2.0,
        output_price_override=10.0,
    )

    assert estimates == [
        estimator.CostEstimate(
            model="custom-model",
            samples=2,
            avg_input_tokens=4.0,
            p50_input_tokens=3.0,
            p95_input_tokens=5.0,
            total_input_tokens=8,
            expected_visible_output_tokens=100,
            expected_reasoning_output_tokens=50,
            total_output_tokens=300,
            input_cost_usd=0.0,
            output_cost_usd=0.003,
            total_cost_usd=0.003,
            batch_total_cost_usd=0.0015,
        )
    ]


def test_markdown_summary_mentions_reasoning_tokens() -> None:
    estimate = estimator.CostEstimate(
        model="gpt-5.4",
        samples=10,
        avg_input_tokens=120.0,
        p50_input_tokens=100.0,
        p95_input_tokens=180.0,
        total_input_tokens=1_200,
        expected_visible_output_tokens=256,
        expected_reasoning_output_tokens=128,
        total_output_tokens=3_840,
        input_cost_usd=0.003,
        output_cost_usd=0.0576,
        total_cost_usd=0.0606,
        batch_total_cost_usd=0.0303,
    )

    markdown = estimator.markdown_summary(
        dataset_label="gsm8k/test",
        estimates=[estimate],
        tokenizer_note="`tiktoken`",
    )

    assert "| `gpt-5.4` | 10 | 120.0 | 180 | 384 | $0.0606 | $0.0303 |" in markdown
    assert "reasoning tokens as output tokens" in markdown
