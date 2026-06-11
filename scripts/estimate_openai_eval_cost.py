#!/usr/bin/env python3
"""Estimate OpenAI API credits needed for common text evals."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

GSM8K_URLS = {
    "test": "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl",
    "train": "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl",
}

DEFAULT_MODEL_PRICES = {
    "gpt-5.5": {"input": 5.00, "cached_input": 0.50, "output": 30.00},
    "gpt-5.4": {"input": 2.50, "cached_input": 0.25, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
    "gpt-5.2": {"input": 1.75, "cached_input": 0.175, "output": 14.00},
    "gpt-5": {"input": 1.25, "cached_input": 0.125, "output": 10.00},
}

SYSTEM_PROMPT = (
    "You are solving a grade-school math word problem. Show concise reasoning, "
    "then put the final numeric answer on a separate line prefixed with ####."
)

USER_TEMPLATE = "Problem:\n{question}\n\nSolve the problem."


@dataclass(frozen=True)
class EvalItem:
    question: str
    answer: str | None = None


@dataclass(frozen=True)
class CostEstimate:
    model: str
    samples: int
    avg_input_tokens: float
    p50_input_tokens: float
    p95_input_tokens: float
    total_input_tokens: int
    expected_visible_output_tokens: int
    expected_reasoning_output_tokens: int
    total_output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    batch_total_cost_usd: float


def load_gsm8k(split: str) -> list[EvalItem]:
    url = GSM8K_URLS[split]
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    return [
        EvalItem(question=row["question"], answer=row.get("answer"))
        for row in parse_jsonl(response.text)
    ]


def load_jsonl(path: Path, question_key: str, answer_key: str | None) -> list[EvalItem]:
    rows = parse_jsonl(path.read_text(encoding="utf-8"))
    return [
        EvalItem(
            question=str(row[question_key]),
            answer=str(row[answer_key]) if answer_key and row.get(answer_key) is not None else None,
        )
        for row in rows
    ]


def parse_jsonl(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def count_tokens(text: str, model: str) -> int:
    try:
        import tiktoken
    except ImportError:
        return estimate_tokens_from_chars(text)

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


def estimate_tokens_from_chars(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def render_input(question: str) -> str:
    return f"{SYSTEM_PROMPT}\n\n{USER_TEMPLATE.format(question=question)}"


def percentile(values: Sequence[int], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil((pct / 100) * len(ordered)) - 1))
    return float(ordered[index])


def estimate_costs(
    *,
    items: Sequence[EvalItem],
    models: Sequence[str],
    visible_output_tokens: int,
    reasoning_output_tokens: int,
    input_price_override: float | None = None,
    output_price_override: float | None = None,
) -> list[CostEstimate]:
    estimates: list[CostEstimate] = []
    for model in models:
        if model not in DEFAULT_MODEL_PRICES and (
            input_price_override is None or output_price_override is None
        ):
            raise ValueError(
                f"No default price for {model}. Pass --input-price-per-mtok and --output-price-per-mtok."
            )

        input_price = (
            input_price_override
            if input_price_override is not None
            else DEFAULT_MODEL_PRICES[model]["input"]
        )
        output_price = (
            output_price_override
            if output_price_override is not None
            else DEFAULT_MODEL_PRICES[model]["output"]
        )
        input_counts = [count_tokens(render_input(item.question), model) for item in items]
        total_input = sum(input_counts)
        per_item_output = visible_output_tokens + reasoning_output_tokens
        total_output = per_item_output * len(items)
        input_cost = total_input / 1_000_000 * input_price
        output_cost = total_output / 1_000_000 * output_price
        total_cost = input_cost + output_cost
        estimates.append(
            CostEstimate(
                model=model,
                samples=len(items),
                avg_input_tokens=round(statistics.fmean(input_counts), 2)
                if input_counts
                else 0.0,
                p50_input_tokens=percentile(input_counts, 50),
                p95_input_tokens=percentile(input_counts, 95),
                total_input_tokens=total_input,
                expected_visible_output_tokens=visible_output_tokens,
                expected_reasoning_output_tokens=reasoning_output_tokens,
                total_output_tokens=total_output,
                input_cost_usd=round(input_cost, 4),
                output_cost_usd=round(output_cost, 4),
                total_cost_usd=round(total_cost, 4),
                batch_total_cost_usd=round(total_cost * 0.5, 4),
            )
        )
    return estimates


def markdown_summary(
    *,
    dataset_label: str,
    estimates: Sequence[CostEstimate],
    tokenizer_note: str,
) -> str:
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# OpenAI eval credit estimate",
        "",
        f"Generated at: `{generated_at}`",
        f"Dataset: `{dataset_label}`",
        f"Token counting: {tokenizer_note}",
        "",
        "| Model | Samples | Avg input tok | P95 input tok | Output tok/sample | Standard cost | Batch cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for estimate in estimates:
        output_per_sample = (
            estimate.expected_visible_output_tokens
            + estimate.expected_reasoning_output_tokens
        )
        lines.append(
            "| `{model}` | {samples} | {avg:,.1f} | {p95:,.0f} | {out:,} | ${standard:,.4f} | ${batch:,.4f} |".format(
                model=estimate.model,
                samples=estimate.samples,
                avg=estimate.avg_input_tokens,
                p95=estimate.p95_input_tokens,
                out=output_per_sample,
                standard=estimate.total_cost_usd,
                batch=estimate.batch_total_cost_usd,
            )
        )
    lines.extend(
        [
            "",
            "Output tokens include the configured visible answer budget plus any configured hidden reasoning-token budget. "
            "OpenAI bills reasoning tokens as output tokens even though they are not visible in API responses.",
        ]
    )
    return "\n".join(lines) + "\n"


def tokenizer_note(models: Sequence[str]) -> str:
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        return "`tiktoken` not installed; using rough character-based estimate."
    return f"`tiktoken` via encoding_for_model for {', '.join(models)}."


def write_outputs(
    *,
    estimates: Sequence[CostEstimate],
    output_dir: Path,
    dataset_label: str,
    tokenizer_note_value: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = output_dir / f"openai_eval_cost_{stamp}.json"
    md_path = output_dir / f"openai_eval_cost_{stamp}.md"
    json_path.write_text(
        json.dumps([asdict(estimate) for estimate in estimates], indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    md_path.write_text(
        markdown_summary(
            dataset_label=dataset_label,
            estimates=estimates,
            tokenizer_note=tokenizer_note_value,
        ),
        encoding="utf-8",
    )
    return json_path, md_path


def maybe_limit(items: Sequence[EvalItem], limit: int | None) -> list[EvalItem]:
    return list(items if limit is None else items[:limit])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate OpenAI API eval cost.")
    parser.add_argument("--dataset", choices=("gsm8k",), default="gsm8k")
    parser.add_argument("--split", choices=("test", "train"), default="test")
    parser.add_argument("--dataset-path", type=Path)
    parser.add_argument("--question-key", default="question")
    parser.add_argument("--answer-key", default="answer")
    parser.add_argument("--model", action="append", default=None)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--visible-output-tokens", type=int, default=256)
    parser.add_argument("--reasoning-output-tokens", type=int, default=256)
    parser.add_argument("--input-price-per-mtok", type=float)
    parser.add_argument("--output-price-per-mtok", type=float)
    parser.add_argument("--output-dir", type=Path, default=Path("result"))
    return parser.parse_args()


def load_items(args: argparse.Namespace) -> tuple[str, list[EvalItem]]:
    if args.dataset_path:
        items = load_jsonl(args.dataset_path, args.question_key, args.answer_key)
        return str(args.dataset_path), maybe_limit(items, args.limit)

    items = load_gsm8k(args.split)
    return f"gsm8k/{args.split}", maybe_limit(items, args.limit)


def main() -> int:
    args = parse_args()
    models = args.model or ["gpt-5.4", "gpt-5.5"]
    dataset_label, items = load_items(args)
    estimates = estimate_costs(
        items=items,
        models=models,
        visible_output_tokens=args.visible_output_tokens,
        reasoning_output_tokens=args.reasoning_output_tokens,
        input_price_override=args.input_price_per_mtok,
        output_price_override=args.output_price_per_mtok,
    )
    note = tokenizer_note(models)
    json_path, md_path = write_outputs(
        estimates=estimates,
        output_dir=args.output_dir,
        dataset_label=dataset_label,
        tokenizer_note_value=note,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(markdown_summary(dataset_label=dataset_label, estimates=estimates, tokenizer_note=note))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
