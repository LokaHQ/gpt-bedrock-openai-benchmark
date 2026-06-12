#!/usr/bin/env python3
"""Score GSM8K benchmark outputs against the original dataset answers."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import unicodedata
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import httpx

GSM8K_TEST_URL = (
    "https://raw.githubusercontent.com/openai/grade-school-math/master/"
    "grade_school_math/data/test.jsonl"
)

FINAL_ANSWER_RE = re.compile(r"####\s*([^\n\r]+)")
NUMBER_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


@dataclass(frozen=True)
class Gsm8kReference:
    prompt_id: str
    answer_text: str


@dataclass(frozen=True)
class AccuracyRunConfig:
    label: str
    benchmark_jsonl: Path
    output_dir: Path


@dataclass(frozen=True)
class AccuracyRecord:
    prompt_id: str
    run_index: int
    provider: str
    model: str
    ok: bool
    prompt_index: int
    reference_answer: str | None
    model_answer: str | None
    normalized_reference_answer: str | None
    normalized_model_answer: str | None
    is_correct: bool
    mismatch_reason: str | None


@dataclass(frozen=True)
class AccuracySummary:
    label: str
    provider: str
    model: str
    benchmark_jsonl: str
    total_records: int
    successful_records: int
    failed_records: int
    scored_records: int
    correct_records: int
    incorrect_records: int
    missing_model_answer_records: int
    missing_reference_answer_records: int
    accuracy_overall: float
    accuracy_success_only: float


MAIN_RUNS = (
    AccuracyRunConfig(
        label="bedrock-medium",
        benchmark_jsonl=Path(
            "result/gsm8k-gpt55-medium/openai_responses_latency_20260610T083101Z.jsonl"
        ),
        output_dir=Path("result/gsm8k-gpt55-medium"),
    ),
    AccuracyRunConfig(
        label="openai-medium",
        benchmark_jsonl=Path(
            "result/openai-gsm8k-gpt55-medium/openai_responses_latency_20260611T111932Z.jsonl"
        ),
        output_dir=Path("result/openai-gsm8k-gpt55-medium"),
    ),
    AccuracyRunConfig(
        label="bedrock-high",
        benchmark_jsonl=Path(
            "result/gsm8k-gpt55-high/openai_responses_latency_20260610T095751Z.jsonl"
        ),
        output_dir=Path("result/gsm8k-gpt55-high"),
    ),
    AccuracyRunConfig(
        label="openai-high",
        benchmark_jsonl=Path(
            "result/openai-gsm8k-gpt55-high/openai_responses_latency_20260611T124720Z.jsonl"
        ),
        output_dir=Path("result/openai-gsm8k-gpt55-high"),
    ),
    AccuracyRunConfig(
        label="bedrock-xhigh",
        benchmark_jsonl=Path(
            "result/gsm8k-gpt55-xhigh/openai_responses_latency_20260610T120008Z.jsonl"
        ),
        output_dir=Path("result/gsm8k-gpt55-xhigh"),
    ),
    AccuracyRunConfig(
        label="openai-xhigh-merged-clean",
        benchmark_jsonl=Path(
            "result/openai-gsm8k-gpt55-xhigh-merged-clean/"
            "openai_responses_latency_20260611T172028Z.jsonl"
        ),
        output_dir=Path("result/openai-gsm8k-gpt55-xhigh-merged-clean"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score GSM8K benchmark outputs.")
    parser.add_argument(
        "--benchmark-jsonl",
        action="append",
        type=Path,
        help="Benchmark JSONL artifact to score. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for a single --benchmark-jsonl run.",
    )
    parser.add_argument(
        "--main-runs",
        action="store_true",
        help="Score the repo's six main benchmark runs and write per-run outputs.",
    )
    parser.add_argument(
        "--aggregate-output-dir",
        type=Path,
        default=Path("result"),
        help="Where to write the aggregate main-runs summary files.",
    )
    return parser.parse_args()


def parse_jsonl(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def load_gsm8k_test_references() -> dict[str, Gsm8kReference]:
    response = httpx.get(GSM8K_TEST_URL, timeout=30)
    response.raise_for_status()
    references: dict[str, Gsm8kReference] = {}
    for index, row in enumerate(parse_jsonl(response.text)):
        references[f"gsm8k-test-{index}"] = Gsm8kReference(
            prompt_id=f"gsm8k-test-{index}",
            answer_text=str(row["answer"]),
        )
    return references


def extract_final_answer(text: str | None) -> str | None:
    if not text:
        return None
    matches = FINAL_ANSWER_RE.findall(text)
    if not matches:
        return None
    return matches[-1].strip()


def normalize_answer(answer: str | None) -> str | None:
    if answer is None:
        return None
    normalized = unicodedata.normalize("NFKC", answer).strip()
    normalized = normalized.replace("−", "-").replace("$", "")
    normalized = normalized.replace(",", "")
    normalized = normalized.rstrip(".")
    number_match = NUMBER_RE.fullmatch(normalized)
    if number_match:
        try:
            return format_decimal(Decimal(normalized))
        except InvalidOperation:
            return normalized.lower()
    numbers = NUMBER_RE.findall(normalized)
    if len(numbers) == 1:
        try:
            return format_decimal(Decimal(numbers[0].replace(",", "")))
        except InvalidOperation:
            pass
    return " ".join(normalized.lower().split())


def format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f").rstrip("0").rstrip(".")


def score_record(
    row: dict[str, Any],
    references: dict[str, Gsm8kReference],
) -> AccuracyRecord:
    prompt_id = str(row["prompt_id"])
    reference = references.get(prompt_id)
    reference_answer = extract_final_answer(reference.answer_text) if reference else None
    model_answer = extract_final_answer(row.get("output_text"))
    normalized_reference = normalize_answer(reference_answer)
    normalized_model = normalize_answer(model_answer)
    mismatch_reason: str | None = None
    is_correct = False

    if not row.get("ok", False):
        mismatch_reason = "request_failed"
    elif normalized_reference is None:
        mismatch_reason = "missing_reference_answer"
    elif normalized_model is None:
        mismatch_reason = "missing_model_answer"
    elif normalized_reference == normalized_model:
        is_correct = True
    else:
        mismatch_reason = "answer_mismatch"

    return AccuracyRecord(
        prompt_id=prompt_id,
        run_index=int(row["run_index"]),
        provider=str(row["provider"]),
        model=str(row["model"]),
        ok=bool(row["ok"]),
        prompt_index=int(row["prompt_index"]),
        reference_answer=reference_answer,
        model_answer=model_answer,
        normalized_reference_answer=normalized_reference,
        normalized_model_answer=normalized_model,
        is_correct=is_correct,
        mismatch_reason=mismatch_reason,
    )


def summarize_records(
    *,
    label: str,
    benchmark_jsonl: Path,
    records: list[AccuracyRecord],
) -> AccuracySummary:
    total_records = len(records)
    successful_records = sum(record.ok for record in records)
    failed_records = total_records - successful_records
    correct_records = sum(record.is_correct for record in records)
    missing_model_answer_records = sum(
        record.mismatch_reason == "missing_model_answer" for record in records
    )
    missing_reference_answer_records = sum(
        record.mismatch_reason == "missing_reference_answer" for record in records
    )
    scored_records = sum(
        record.normalized_reference_answer is not None and record.ok for record in records
    )
    incorrect_records = scored_records - correct_records
    accuracy_overall = round(correct_records / total_records, 4) if total_records else 0.0
    accuracy_success_only = (
        round(correct_records / successful_records, 4) if successful_records else 0.0
    )
    provider = records[0].provider if records else "unknown"
    model = records[0].model if records else "unknown"
    return AccuracySummary(
        label=label,
        provider=provider,
        model=model,
        benchmark_jsonl=str(benchmark_jsonl),
        total_records=total_records,
        successful_records=successful_records,
        failed_records=failed_records,
        scored_records=scored_records,
        correct_records=correct_records,
        incorrect_records=incorrect_records,
        missing_model_answer_records=missing_model_answer_records,
        missing_reference_answer_records=missing_reference_answer_records,
        accuracy_overall=accuracy_overall,
        accuracy_success_only=accuracy_success_only,
    )


def markdown_summary(
    summary: AccuracySummary,
    mismatches: list[AccuracyRecord],
    generated_at: str,
) -> str:
    lines = [
        "# GSM8K accuracy summary",
        "",
        f"Generated at: `{generated_at}`",
        f"Benchmark artifact: `{summary.benchmark_jsonl}`",
        f"Provider: `{summary.provider}`",
        f"Model: `{summary.model}`",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total rows | {summary.total_records} |",
        f"| Successful rows | {summary.successful_records} |",
        f"| Failed rows | {summary.failed_records} |",
        f"| Correct rows | {summary.correct_records} |",
        f"| Incorrect rows | {summary.incorrect_records} |",
        f"| Missing model answer rows | {summary.missing_model_answer_records} |",
        f"| Missing reference answer rows | {summary.missing_reference_answer_records} |",
        f"| Accuracy over all rows | {format_percent(summary.accuracy_overall)} |",
        f"| Accuracy over successful rows | {format_percent(summary.accuracy_success_only)} |",
        "",
        "Accuracy is computed by extracting the final `####` answer from the original GSM8K test set and from each saved model response, then comparing normalized final answers.",
    ]

    if mismatches:
        lines.extend(
            [
                "",
                "## Sample mismatches",
                "",
                "| Prompt ID | Run | Reason | Expected | Model |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for record in mismatches[:10]:
            lines.append(
                "| {prompt_id} | {run_index} | {reason} | `{expected}` | `{model}` |".format(
                    prompt_id=record.prompt_id,
                    run_index=record.run_index,
                    reason=record.mismatch_reason or "n/a",
                    expected=truncate(record.reference_answer),
                    model=truncate(record.model_answer),
                )
            )
    return "\n".join(lines) + "\n"


def truncate(value: str | None, limit: int = 60) -> str:
    if value is None:
        return "n/a"
    compact = " ".join(value.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def write_run_outputs(
    *,
    output_dir: Path,
    summary: AccuracySummary,
    records: list[AccuracyRecord],
    generated_at: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "gsm8k_accuracy_summary.json"
    md_path = output_dir / "gsm8k_accuracy_summary.md"
    incorrect_records = [record for record in records if not record.is_correct]
    payload = {
        "generated_at": generated_at,
        "summary": asdict(summary),
        "records": [asdict(record) for record in records],
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(
        markdown_summary(summary, incorrect_records, generated_at),
        encoding="utf-8",
    )
    return json_path, md_path


def aggregate_markdown(
    summaries: list[AccuracySummary],
    generated_at: str,
) -> str:
    lines = [
        "# GSM8K accuracy comparison",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "| Label | Provider | Model | Correct | Incorrect | Accuracy (all) | Accuracy (successful) |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        lines.append(
            "| {label} | {provider} | `{model}` | {correct} | {incorrect} | {overall} | {success} |".format(
                label=summary.label,
                provider=summary.provider,
                model=summary.model,
                correct=summary.correct_records,
                incorrect=summary.incorrect_records,
                overall=format_percent(summary.accuracy_overall),
                success=format_percent(summary.accuracy_success_only),
            )
        )

    grouped: dict[str, list[AccuracySummary]] = {}
    for summary in summaries:
        effort = summary.label.split("-", 1)[1].replace("-merged-clean", "")
        grouped.setdefault(effort, []).append(summary)

    lines.extend(["", "## Bedrock vs OpenAI deltas", ""])
    for effort, pair in grouped.items():
        if len(pair) != 2:
            continue
        pair_by_provider = {summary.provider: summary for summary in pair}
        bedrock = pair_by_provider.get("bedrock")
        openai = pair_by_provider.get("openai")
        if not bedrock or not openai:
            continue
        delta = round(openai.accuracy_overall - bedrock.accuracy_overall, 4)
        lines.append(
            "- `{effort}`: OpenAI {openai_acc} vs Bedrock {bedrock_acc} "
            "({delta:+.2f} percentage points).".format(
                effort=effort,
                openai_acc=format_percent(openai.accuracy_overall),
                bedrock_acc=format_percent(bedrock.accuracy_overall),
                delta=delta * 100,
            )
        )

    lines.append("")
    return "\n".join(lines)


def score_run(
    *,
    label: str,
    benchmark_jsonl: Path,
    output_dir: Path,
    references: dict[str, Gsm8kReference],
    generated_at: str,
) -> AccuracySummary:
    rows = parse_jsonl(benchmark_jsonl.read_text(encoding="utf-8"))
    records = [score_record(row, references) for row in rows]
    summary = summarize_records(label=label, benchmark_jsonl=benchmark_jsonl, records=records)
    write_run_outputs(
        output_dir=output_dir,
        summary=summary,
        records=records,
        generated_at=generated_at,
    )
    return summary


def run_main_runs(
    *,
    aggregate_output_dir: Path,
    references: dict[str, Gsm8kReference],
    generated_at: str,
) -> list[AccuracySummary]:
    summaries = [
        score_run(
            label=config.label,
            benchmark_jsonl=config.benchmark_jsonl,
            output_dir=config.output_dir,
            references=references,
            generated_at=generated_at,
        )
        for config in MAIN_RUNS
    ]
    aggregate_output_dir.mkdir(parents=True, exist_ok=True)
    aggregate_json = aggregate_output_dir / "gsm8k_accuracy_main_runs.json"
    aggregate_md = aggregate_output_dir / "gsm8k_accuracy_main_runs.md"
    aggregate_json.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "summaries": [asdict(summary) for summary in summaries],
                "mean_accuracy_overall": round(
                    statistics.fmean(summary.accuracy_overall for summary in summaries),
                    4,
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    aggregate_md.write_text(aggregate_markdown(summaries, generated_at), encoding="utf-8")
    return summaries


def main() -> int:
    args = parse_args()
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    references = load_gsm8k_test_references()

    if args.main_runs:
        run_main_runs(
            aggregate_output_dir=args.aggregate_output_dir,
            references=references,
            generated_at=generated_at,
        )

    if args.benchmark_jsonl:
        if len(args.benchmark_jsonl) > 1 and args.output_dir is not None:
            raise SystemExit("--output-dir only supports a single --benchmark-jsonl input.")
        for benchmark_jsonl in args.benchmark_jsonl:
            output_dir = args.output_dir or benchmark_jsonl.parent
            score_run(
                label=benchmark_jsonl.parent.name,
                benchmark_jsonl=benchmark_jsonl,
                output_dir=output_dir,
                references=references,
                generated_at=generated_at,
            )

    if not args.main_runs and not args.benchmark_jsonl:
        raise SystemExit("Pass --main-runs or at least one --benchmark-jsonl path.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
