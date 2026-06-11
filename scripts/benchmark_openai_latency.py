#!/usr/bin/env python3
"""Measure streaming latency for OpenAI-compatible Responses API endpoints."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import botocore.session
import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import ReadOnlyCredentials
from botocore.exceptions import BotoCoreError
from dotenv import load_dotenv

DEFAULT_BEDROCK_MODELS = ("openai.gpt-5.5", "openai.gpt-5.4")
DEFAULT_OPENAI_MODELS = ("gpt-5.5", "gpt-5.4")
DEFAULT_OPENAI_PRICES_PER_MTOK = {
    "gpt-5.5": {"input": 5.00, "output": 30.00},
    "gpt-5.4": {"input": 2.50, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
    "gpt-5.2": {"input": 1.75, "output": 14.00},
    "gpt-5": {"input": 1.25, "output": 10.00},
}
DEFAULT_PROMPTS = (
    "In exactly five concise bullets, explain why streaming latency matters for enterprise AI assistants.",
    "Summarize the tradeoffs between model capability, time-to-first-token, and total latency in one short paragraph.",
    "Return a compact JSON object with keys metric, definition, and caveat for time-to-first-token.",
)
GSM8K_URLS = {
    "test": "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl",
    "train": "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl",
}

AGGREGATE_METRICS = (
    ("ttfb_ms", "time_to_first_byte_ms"),
    ("ttft_ms", "time_to_first_token_ms"),
    ("total_ms", "end_to_end_latency_ms"),
    ("output_tokens_per_second", "request_output_throughput_token_per_s"),
    ("input_tokens", "number_input_tokens"),
    ("output_tokens", "number_output_tokens"),
    ("reasoning_tokens", "number_reasoning_tokens"),
    ("estimated_openai_cost_usd", "estimated_openai_cost_usd"),
)


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    auth_mode: str
    api_key: str | None = None
    aws_credentials: ReadOnlyCredentials | None = None
    region: str | None = None


@dataclass(frozen=True)
class PromptItem:
    prompt_id: str
    prompt_text: str
    expected_answer: str | None = None


@dataclass
class BenchmarkRecord:
    provider: str
    model: str
    run_index: int
    prompt_index: int
    started_at: str
    ok: bool
    prompt_id: str | None = None
    prompt_text: str | None = None
    expected_answer: str | None = None
    ttfb_ms: float | None = None
    ttft_ms: float | None = None
    total_ms: float | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    input_tokens: int | None = None
    output_text: str | None = None
    output_chars: int = 0
    output_tokens_per_second: float | None = None
    output_chars_per_second: float | None = None
    estimated_openai_cost_usd: float | None = None
    request_id: str | None = None
    error: str | None = None


def load_environment() -> None:
    """Load local env files without requiring them."""
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".codex" / ".env", override=False)


def provider_config(provider: str, region: str) -> ProviderConfig:
    if provider == "bedrock":
        key = os.getenv("BEDROCK_OPENAI_API_KEY") or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        base_url = os.getenv(
            "BEDROCK_OPENAI_BASE_URL",
            f"https://bedrock-mantle.{region}.api.aws/openai/v1",
        ).rstrip("/")
        if key:
            return ProviderConfig(
                name="bedrock",
                base_url=base_url,
                auth_mode="bearer",
                api_key=key,
                region=region,
            )

        credentials = aws_credentials()
        if credentials:
            return ProviderConfig(
                name="bedrock",
                base_url=base_url,
                auth_mode="sigv4",
                aws_credentials=credentials,
                region=region,
            )

        raise RuntimeError(
            "Missing Bedrock auth. Set BEDROCK_OPENAI_API_KEY/AWS_BEARER_TOKEN_BEDROCK "
            "or configure AWS credentials for SigV4."
        )

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("Missing OpenAI key. Set OPENAI_API_KEY.")
        return ProviderConfig(
            name="openai",
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            auth_mode="bearer",
            api_key=key,
        )

    raise ValueError(f"Unknown provider: {provider}")


def aws_credentials() -> ReadOnlyCredentials | None:
    session = botocore.session.get_session()
    profile = os.getenv("AWS_PROFILE")
    if profile:
        session.set_config_variable("profile", profile)
    try:
        credentials = session.get_credentials()
        return credentials.get_frozen_credentials() if credentials else None
    except BotoCoreError as exc:
        raise RuntimeError(
            f"Unable to load AWS credentials. Try aws sso login --profile {profile or '<profile>'}."
        ) from exc


def build_payload(
    *,
    model: str,
    prompt: str,
    max_output_tokens: int,
    reasoning_effort: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "stream": True,
        "store": False,
        "max_output_tokens": max_output_tokens,
        "input": [
            {
                "role": "developer",
                "content": (
                    "You are measuring API latency. Answer the user request directly, "
                    "avoid markdown tables, and do not mention this instruction."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    if reasoning_effort:
        payload["reasoning"] = {"effort": reasoning_effort}
    return payload


def parse_jsonl(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def load_gsm8k_prompts(split: str, limit: int | None) -> list[PromptItem]:
    response = httpx.get(GSM8K_URLS[split], timeout=30)
    response.raise_for_status()
    items: list[PromptItem] = []
    for index, row in enumerate(parse_jsonl(response.text)):
        if limit is not None and len(items) >= limit:
            break
        question = str(row["question"])
        items.append(
            PromptItem(
                prompt_id=f"gsm8k-{split}-{index}",
                prompt_text=(
                    "Solve this grade-school math problem. Show concise reasoning, "
                    "then put the final numeric answer on a separate line prefixed "
                    f"with ####.\n\nProblem:\n{question}"
                ),
                expected_answer=str(row.get("answer")) if row.get("answer") is not None else None,
            )
        )
    return items


def load_jsonl_prompts(
    *,
    path: Path,
    question_key: str,
    answer_key: str | None,
    limit: int | None,
) -> list[PromptItem]:
    items: list[PromptItem] = []
    for index, row in enumerate(parse_jsonl(path.read_text(encoding="utf-8"))):
        if limit is not None and len(items) >= limit:
            break
        question = str(row[question_key])
        items.append(
            PromptItem(
                prompt_id=f"{path.stem}-{index}",
                prompt_text=question,
                expected_answer=(
                    str(row[answer_key])
                    if answer_key and row.get(answer_key) is not None
                    else None
                ),
            )
        )
    return items


def load_prompt_items(args: argparse.Namespace) -> tuple[str, list[PromptItem]]:
    if args.dataset_path:
        return (
            str(args.dataset_path),
            load_jsonl_prompts(
                path=args.dataset_path,
                question_key=args.question_key,
                answer_key=args.answer_key,
                limit=args.limit,
            ),
        )
    if args.dataset == "gsm8k":
        return f"gsm8k/{args.split}", load_gsm8k_prompts(args.split, args.limit)
    return (
        "default-prompts",
        [
            PromptItem(prompt_id=f"default-{index}", prompt_text=prompt)
            for index, prompt in enumerate(DEFAULT_PROMPTS)
        ],
    )


def extract_output_delta(event_data: dict[str, Any]) -> str:
    event_type = str(event_data.get("type", ""))
    delta = event_data.get("delta")
    if event_type.endswith(".delta") and isinstance(delta, str):
        return delta
    if event_type == "response.output_text.delta" and isinstance(delta, str):
        return delta
    return ""


def extract_usage(event_data: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    response = event_data.get("response")
    usage: Any = None
    if isinstance(response, dict):
        usage = response.get("usage")
    if usage is None:
        usage = event_data.get("usage")
    if not isinstance(usage, dict):
        return None, None, None

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    output_details = usage.get("output_tokens_details")
    reasoning_tokens = (
        output_details.get("reasoning_tokens")
        if isinstance(output_details, dict)
        else None
    )
    return (
        input_tokens if isinstance(input_tokens, int) else None,
        output_tokens if isinstance(output_tokens, int) else None,
        reasoning_tokens if isinstance(reasoning_tokens, int) else None,
    )


def extract_stream_error(event_data: dict[str, Any]) -> str | None:
    event_type = str(event_data.get("type", ""))
    if event_type != "error" and not event_type.endswith(".failed"):
        return None

    error = event_data.get("error")
    response = event_data.get("response")
    if not isinstance(error, dict) and isinstance(response, dict):
        error = response.get("error")
    if isinstance(error, dict):
        code = error.get("code")
        message = error.get("message")
        if code and message:
            return f"{code}: {message}"
        if message:
            return str(message)
        if code:
            return str(code)
    if isinstance(error, str):
        return error
    return event_type


def run_once(
    *,
    client: httpx.Client,
    provider: ProviderConfig,
    model: str,
    prompt_item: PromptItem,
    prompt_index: int,
    run_index: int,
    max_output_tokens: int,
    reasoning_effort: str | None,
    timeout_seconds: float,
) -> BenchmarkRecord:
    request_id = str(uuid4())
    record = BenchmarkRecord(
        provider=provider.name,
        model=model,
        run_index=run_index,
        prompt_index=prompt_index,
        started_at=datetime.now(UTC).isoformat(),
        ok=False,
        request_id=request_id,
        prompt_id=prompt_item.prompt_id,
        prompt_text=prompt_item.prompt_text,
        expected_answer=prompt_item.expected_answer,
    )
    payload = build_payload(
        model=model,
        prompt=prompt_item.prompt_text,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
    )
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Client-Request-Id": request_id,
    }
    endpoint = f"{provider.base_url.rstrip('/')}/responses"
    headers = auth_headers(
        provider=provider,
        method="POST",
        endpoint=endpoint,
        headers=headers,
        body=body,
    )

    start = time.perf_counter()
    first_byte_at: float | None = None
    first_token_at: float | None = None
    output_chars = 0
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    output_parts: list[str] = []

    try:
        with client.stream(
            "POST",
            endpoint,
            headers=headers,
            content=body,
            timeout=timeout_seconds,
        ) as response:
            if response.status_code >= 400:
                response_text = read_error_response(response)
                record.total_ms = to_ms(time.perf_counter() - start)
                record.error = f"HTTP {response.status_code}: {truncate(response_text)}"
                return record
            for line in response.iter_lines():
                if not line:
                    continue
                now = time.perf_counter()
                if first_byte_at is None:
                    first_byte_at = now
                if not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    continue
                try:
                    event_data = json.loads(data)
                except json.JSONDecodeError:
                    continue

                stream_error = extract_stream_error(event_data)
                if stream_error:
                    record.total_ms = to_ms(time.perf_counter() - start)
                    record.error = truncate(stream_error)
                    return record

                delta = extract_output_delta(event_data)
                if delta:
                    output_parts.append(delta)
                    output_chars += len(delta)
                    if first_token_at is None:
                        first_token_at = now

                maybe_input_tokens, maybe_output_tokens, maybe_reasoning_tokens = (
                    extract_usage(event_data)
                )
                input_tokens = maybe_input_tokens if maybe_input_tokens is not None else input_tokens
                output_tokens = (
                    maybe_output_tokens if maybe_output_tokens is not None else output_tokens
                )
                reasoning_tokens = (
                    maybe_reasoning_tokens
                    if maybe_reasoning_tokens is not None
                    else reasoning_tokens
                )

        total_seconds = time.perf_counter() - start
        record.ok = True
        record.ttfb_ms = to_ms(first_byte_at - start) if first_byte_at else None
        record.ttft_ms = to_ms(first_token_at - start) if first_token_at else None
        record.total_ms = to_ms(total_seconds)
        record.output_chars = output_chars
        record.input_tokens = input_tokens
        record.output_tokens = output_tokens
        record.reasoning_tokens = reasoning_tokens
        record.output_text = "".join(output_parts) if output_parts else None
        if output_tokens is not None and total_seconds > 0:
            record.output_tokens_per_second = round(output_tokens / total_seconds, 2)
        if output_chars and total_seconds > 0:
            record.output_chars_per_second = round(output_chars / total_seconds, 2)
    except Exception as exc:  # noqa: BLE001 - this is a CLI benchmark; record failures.
        record.total_ms = to_ms(time.perf_counter() - start)
        record.error = truncate(str(exc))

    return record


def auth_headers(
    *,
    provider: ProviderConfig,
    method: str,
    endpoint: str,
    headers: dict[str, str],
    body: bytes,
) -> dict[str, str]:
    if provider.auth_mode == "bearer":
        if not provider.api_key:
            raise RuntimeError("Bearer auth selected without an API key.")
        return {**headers, "Authorization": f"Bearer {provider.api_key}"}

    if provider.auth_mode == "sigv4":
        if not provider.aws_credentials or not provider.region:
            raise RuntimeError("SigV4 auth selected without AWS credentials and region.")
        request = AWSRequest(method=method, url=endpoint, data=body, headers=headers)
        SigV4Auth(provider.aws_credentials, "bedrock-mantle", provider.region).add_auth(
            request
        )
        return dict(request.headers)

    raise ValueError(f"Unknown auth mode: {provider.auth_mode}")


def debug_auth(provider: ProviderConfig) -> None:
    sample_endpoint = f"{provider.base_url.rstrip('/')}/responses"
    sample_headers = auth_headers(
        provider=provider,
        method="POST",
        endpoint=sample_endpoint,
        headers={"Content-Type": "application/json", "X-Client-Request-Id": "debug"},
        body=b"{}",
    )
    safe_header_names = sorted(sample_headers)
    print(f"auth_mode={provider.auth_mode}")
    print(f"base_url={provider.base_url}")
    print(f"region={provider.region or 'n/a'}")
    print("sigv4_service=bedrock-mantle" if provider.auth_mode == "sigv4" else "sigv4_service=n/a")
    print(f"signed_header_names={', '.join(safe_header_names)}")


def read_error_response(response: httpx.Response) -> str:
    try:
        content = response.read()
    except httpx.ResponseNotRead:
        return "<streaming error response was not readable>"
    except Exception as exc:  # noqa: BLE001 - best-effort error reporting.
        return f"<failed to read error response: {exc}>"
    return content.decode(response.encoding or "utf-8", errors="replace")


def to_ms(seconds: float) -> float:
    return round(seconds * 1000, 2)


def truncate(value: str, limit: int = 1_500) -> str:
    value = value.replace("\n", " ").strip()
    return value if len(value) <= limit else value[: limit - 1] + "..."


def percentile(values: Sequence[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil((pct / 100) * len(ordered)) - 1))
    return round(ordered[index], 2)


def mean(values: Sequence[float]) -> float | None:
    return round(statistics.fmean(values), 2) if values else None


def stddev(values: Sequence[float]) -> float | None:
    return round(statistics.stdev(values), 2) if len(values) > 1 else None


def metric_distribution(values: Sequence[float]) -> dict[str, float | None]:
    if not values:
        return {
            "count": 0,
            "p25": None,
            "p50": None,
            "p75": None,
            "p90": None,
            "p95": None,
            "p99": None,
            "mean": None,
            "min": None,
            "max": None,
            "stddev": None,
        }
    return {
        "count": len(values),
        "p25": percentile(values, 25),
        "p50": percentile(values, 50),
        "p75": percentile(values, 75),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "mean": mean(values),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "stddev": stddev(values),
    }


def canonical_openai_model(model: str) -> str:
    return model.removeprefix("openai.")


def model_price_per_mtok(
    *,
    model: str,
    token_type: str,
    override: float | None,
) -> float | None:
    if override is not None:
        return override
    prices = DEFAULT_OPENAI_PRICES_PER_MTOK.get(canonical_openai_model(model))
    if not prices:
        return None
    return prices[token_type]


def estimate_openai_cost(
    *,
    record: BenchmarkRecord,
    input_price_per_mtok: float | None,
    output_price_per_mtok: float | None,
) -> float | None:
    if record.input_tokens is None or record.output_tokens is None:
        return None
    input_price = model_price_per_mtok(
        model=record.model,
        token_type="input",
        override=input_price_per_mtok,
    )
    output_price = model_price_per_mtok(
        model=record.model,
        token_type="output",
        override=output_price_per_mtok,
    )
    if input_price is None or output_price is None:
        return None
    return round(
        (record.input_tokens / 1_000_000 * input_price)
        + (record.output_tokens / 1_000_000 * output_price),
        6,
    )


def billable_tokens(record: BenchmarkRecord) -> int | None:
    if record.input_tokens is None or record.output_tokens is None:
        return None
    return record.input_tokens + record.output_tokens


def summarize(records: Iterable[BenchmarkRecord]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[BenchmarkRecord]] = {}
    for record in records:
        grouped.setdefault((record.provider, record.model), []).append(record)

    summary: list[dict[str, Any]] = []
    for (provider, model), group in sorted(grouped.items()):
        successful = [record for record in group if record.ok]
        row: dict[str, Any] = {
            "provider": provider,
            "model": model,
            "successful_runs": len(successful),
            "failed_runs": len(group) - len(successful),
        }
        for metric in (
            "ttfb_ms",
            "ttft_ms",
            "total_ms",
            "input_tokens",
            "output_tokens",
            "reasoning_tokens",
            "output_tokens_per_second",
        ):
            values = [
                value
                for record in successful
                if (value := getattr(record, metric)) is not None
            ]
            row[f"{metric}_avg"] = mean(values)
            row[f"{metric}_p50"] = percentile(values, 50)
            row[f"{metric}_p90"] = percentile(values, 90)
            row[f"{metric}_p95"] = percentile(values, 95)
        costs = [
            record.estimated_openai_cost_usd
            for record in successful
            if record.estimated_openai_cost_usd is not None
        ]
        row["estimated_openai_cost_usd_total"] = round(sum(costs), 6) if costs else None
        summary.append(row)
    return summary


def aggregate_metrics(records: Iterable[BenchmarkRecord]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[BenchmarkRecord]] = {}
    for record in records:
        grouped.setdefault((record.provider, record.model), []).append(record)

    aggregates: list[dict[str, Any]] = []
    for (provider, model), group in sorted(grouped.items()):
        successful = [record for record in group if record.ok]
        metric_rows: dict[str, dict[str, float | None]] = {}
        for attr_name, metric_name in AGGREGATE_METRICS:
            values = [
                value
                for record in successful
                if (value := getattr(record, attr_name)) is not None
            ]
            metric_rows[metric_name] = metric_distribution(values)

        total_output_tokens = sum(
            record.output_tokens or 0 for record in successful
        )
        total_latency_seconds = sum(
            (record.total_ms or 0) / 1000 for record in successful
        )
        overall_output_throughput = (
            round(total_output_tokens / total_latency_seconds, 2)
            if total_latency_seconds > 0
            else None
        )
        estimated_costs = [
            record.estimated_openai_cost_usd
            for record in successful
            if record.estimated_openai_cost_usd is not None
        ]
        estimated_openai_cost_total = (
            round(sum(estimated_costs), 6) if estimated_costs else None
        )
        estimated_openai_cost_mean = (
            round(statistics.fmean(estimated_costs), 6) if estimated_costs else None
        )
        total_wall_seconds = elapsed_wall_seconds(successful)
        completed_requests_per_minute = (
            round(len(successful) / (total_wall_seconds / 60), 2)
            if total_wall_seconds and total_wall_seconds > 0
            else None
        )

        aggregates.append(
            {
                "provider": provider,
                "model": model,
                "number_completed_requests": len(successful),
                "number_errored_requests": len(group) - len(successful),
                "overall_output_throughput_token_per_s": overall_output_throughput,
                "completed_requests_per_minute": completed_requests_per_minute,
                "estimated_openai_cost_usd_total": estimated_openai_cost_total,
                "estimated_openai_cost_usd_mean": estimated_openai_cost_mean,
                "metrics": metric_rows,
            }
        )
    return aggregates


def elapsed_wall_seconds(records: Sequence[BenchmarkRecord]) -> float | None:
    timestamps: list[datetime] = []
    for record in records:
        try:
            timestamps.append(datetime.fromisoformat(record.started_at))
        except ValueError:
            continue
    if len(timestamps) < 2:
        return None
    return (max(timestamps) - min(timestamps)).total_seconds()


def markdown_summary(
    *,
    records: Sequence[BenchmarkRecord],
    summary: Sequence[dict[str, Any]],
    aggregates: Sequence[dict[str, Any]],
    dataset_label: str,
    region: str,
    warmups: int,
    measured_runs: int,
    max_output_tokens: int,
    reasoning_effort: str | None,
) -> str:
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# OpenAI-compatible Responses API latency benchmark",
        "",
        f"Generated at: `{generated_at}`",
        f"Dataset: `{dataset_label}`",
        f"Bedrock region: `{region}`",
        f"Warmups per model: `{warmups}`",
        f"Measured runs per model: `{measured_runs}`",
        f"Max output tokens: `{max_output_tokens}`",
        f"Reasoning effort: `{reasoning_effort or 'provider default'}`",
        "",
        "## Summary",
        "",
        "| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary:
        lines.append(
            "| {provider} | `{model}` | {ok} | {failed} | {ttfb} | {ttft} | {total} | {input_tokens} | {output_tokens} | {reasoning} | {cost} |".format(
                provider=row["provider"],
                model=row["model"],
                ok=row["successful_runs"],
                failed=row["failed_runs"],
                ttfb=format_ms(row["ttfb_ms_p50"]),
                ttft=format_ms(row["ttft_ms_p50"]),
                total=format_ms(row["total_ms_p50"]),
                input_tokens=format_integer(row["input_tokens_p50"]),
                output_tokens=format_integer(row["output_tokens_p50"]),
                reasoning=format_integer(row["reasoning_tokens_p50"]),
                cost=format_usd(row["estimated_openai_cost_usd_total"]),
            )
        )

    if aggregates:
        lines.extend(["", "## LLMPerf-style aggregate metrics", ""])
        for aggregate in aggregates:
            lines.extend(
                [
                    f"### {aggregate['provider']} `{aggregate['model']}`",
                    "",
                    f"Completed requests: `{aggregate['number_completed_requests']}`",
                    f"Errored requests: `{aggregate['number_errored_requests']}`",
                    f"Overall output throughput: `{format_number(aggregate['overall_output_throughput_token_per_s'])}` tokens/s",
                    f"Completed requests per minute: `{format_number(aggregate['completed_requests_per_minute'])}`",
                    f"Estimated OpenAI-equivalent cost total: `{format_usd(aggregate['estimated_openai_cost_usd_total'])}`",
                    f"Estimated OpenAI-equivalent cost mean/request: `{format_usd(aggregate['estimated_openai_cost_usd_mean'])}`",
                    "",
                    "| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for metric_name, stats in aggregate["metrics"].items():
                lines.append(
                    "| {metric} | {p50} | {p90} | {p95} | {mean} | {minimum} | {maximum} | {stddev_value} |".format(
                        metric=metric_name,
                        p50=format_number(stats["p50"]),
                        p90=format_number(stats["p90"]),
                        p95=format_number(stats["p95"]),
                        mean=format_number(stats["mean"]),
                        minimum=format_number(stats["min"]),
                        maximum=format_number(stats["max"]),
                        stddev_value=format_number(stats["stddev"]),
                    )
                )
            lines.append("")

    failed = [record for record in records if not record.ok]
    if failed:
        lines.extend(["", "## Failures", ""])
        for record in failed[:10]:
            lines.append(
                f"- `{record.provider}` `{record.model}` run {record.run_index}: {record.error}"
            )
        if len(failed) > 10:
            lines.append(f"- ...and {len(failed) - 10} more failures.")

    lines.extend(
        [
            "",
            "## Method",
            "",
            "TTFB is measured from request start to the first non-empty streamed line. "
            "TTFT is measured from request start to the first streamed output-text delta. "
            "Total latency is measured through stream completion. Runs are sequential by default "
            "to avoid measuring client-side concurrency effects.",
        ]
    )
    return "\n".join(lines) + "\n"


def format_ms(value: float | None) -> str:
    return "n/a" if value is None else f"{value:,.0f} ms"


def format_number(value: float | None) -> str:
    return "n/a" if value is None else f"{value:,.2f}"


def format_integer(value: float | None) -> str:
    return "n/a" if value is None else f"{value:,.0f}"


def format_usd(value: float | None) -> str:
    return "n/a" if value is None else f"${value:,.4f}"


def write_outputs(
    *,
    records: Sequence[BenchmarkRecord],
    summary_rows: Sequence[dict[str, Any]],
    aggregate_rows: Sequence[dict[str, Any]],
    dataset_label: str,
    output_dir: Path,
    region: str,
    warmups: int,
    measured_runs: int,
    max_output_tokens: int,
    reasoning_effort: str | None,
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path = output_dir / f"openai_responses_latency_{stamp}.jsonl"
    summary_json_path = output_dir / f"openai_responses_latency_{stamp}_summary.json"
    md_path = output_dir / f"openai_responses_latency_{stamp}.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")

    summary_json_path.write_text(
        json.dumps(
            {
                "summary": summary_rows,
                "aggregates": aggregate_rows,
                "dataset": dataset_label,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    md_path.write_text(
        markdown_summary(
            records=records,
            summary=summary_rows,
            aggregates=aggregate_rows,
            dataset_label=dataset_label,
            region=region,
            warmups=warmups,
            measured_runs=measured_runs,
            max_output_tokens=max_output_tokens,
            reasoning_effort=reasoning_effort,
        ),
        encoding="utf-8",
    )
    return jsonl_path, summary_json_path, md_path


def write_partial_record(path: Path | None, record: BenchmarkRecord) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark streaming latency for OpenAI-compatible Responses APIs."
    )
    parser.add_argument(
        "--provider",
        choices=("bedrock", "openai"),
        action="append",
        default=None,
        help="Provider to benchmark. Can be passed more than once.",
    )
    parser.add_argument("--region", default=os.getenv("BEDROCK_REGION", "us-east-2"))
    parser.add_argument("--model", action="append", default=None)
    parser.add_argument("--runs", type=int, default=10, help="Measured runs per model.")
    parser.add_argument("--warmups", type=int, default=2, help="Warmup runs per model.")
    parser.add_argument(
        "--dataset",
        choices=("gsm8k",),
        help="Run every row from a built-in dataset once instead of cycling sample prompts.",
    )
    parser.add_argument("--split", choices=("test", "train"), default="test")
    parser.add_argument("--dataset-path", type=Path)
    parser.add_argument("--question-key", default="question")
    parser.add_argument("--answer-key", default="answer")
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit dataset rows for a pilot run. Omit for the full split.",
    )
    parser.add_argument("--max-output-tokens", type=int, default=180)
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--timeout-seconds", type=float, default=180)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of measured requests to keep in flight. Warmups remain sequential.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("result"))
    parser.add_argument(
        "--max-billable-tokens",
        type=int,
        help="Stop after cumulative input+output tokens across all live calls reaches this cap.",
    )
    parser.add_argument(
        "--max-estimated-openai-cost-usd",
        type=float,
        help="Stop after cumulative OpenAI-equivalent token cost reaches this cap.",
    )
    parser.add_argument(
        "--max-consecutive-missing-usage",
        type=int,
        default=0,
        help=(
            "Stop after this many consecutive OK measured responses omit token usage. "
            "Use 0 to disable."
        ),
    )
    parser.add_argument(
        "--input-price-per-mtok",
        type=float,
        help="Override input price per 1M tokens for cost estimates.",
    )
    parser.add_argument(
        "--output-price-per-mtok",
        type=float,
        help="Override output price per 1M tokens for cost estimates.",
    )
    parser.add_argument(
        "--auth-debug",
        action="store_true",
        help="Print auth mode, endpoint, and signed header names without making model calls.",
    )
    return parser.parse_args()


def models_for(provider: str, requested: Sequence[str] | None) -> Sequence[str]:
    if requested:
        return requested
    return DEFAULT_BEDROCK_MODELS if provider == "bedrock" else DEFAULT_OPENAI_MODELS


def run_status_line(
    *,
    record: BenchmarkRecord,
    index: int,
    total_runs: int,
    cumulative_billable_tokens: int,
    cumulative_estimated_cost: float,
) -> str:
    status = "ok" if record.ok else "failed"
    token_text = (
        "tokens unavailable"
        if record.input_tokens is None or record.output_tokens is None
        else (
            f"in={record.input_tokens:,} out={record.output_tokens:,} "
            f"reasoning={format_integer(record.reasoning_tokens)}"
        )
    )
    cost_text = (
        "cost=n/a"
        if record.estimated_openai_cost_usd is None
        else f"cost=${record.estimated_openai_cost_usd:.6f}"
    )
    return (
        f"{record.provider} {record.model} run {index}/{total_runs}: {status}; "
        f"{token_text}; {cost_text}; "
        f"cumulative_tokens={cumulative_billable_tokens:,}; "
        f"cumulative_est_openai_cost=${cumulative_estimated_cost:.6f}"
    )


def with_estimated_cost(
    *,
    record: BenchmarkRecord,
    input_price_per_mtok: float | None,
    output_price_per_mtok: float | None,
) -> BenchmarkRecord:
    record.estimated_openai_cost_usd = estimate_openai_cost(
        record=record,
        input_price_per_mtok=input_price_per_mtok,
        output_price_per_mtok=output_price_per_mtok,
    )
    return record


def update_cumulative_usage(
    *,
    record: BenchmarkRecord,
    cumulative_billable_tokens: int,
    cumulative_estimated_cost: float,
) -> tuple[int, float]:
    current_billable_tokens = billable_tokens(record)
    if current_billable_tokens is not None:
        cumulative_billable_tokens += current_billable_tokens
    if record.estimated_openai_cost_usd is not None:
        cumulative_estimated_cost += record.estimated_openai_cost_usd
    return cumulative_billable_tokens, cumulative_estimated_cost


def cap_stop_reason(
    *,
    cumulative_billable_tokens: int,
    cumulative_estimated_cost: float,
    max_billable_tokens: int | None,
    max_estimated_openai_cost_usd: float | None,
) -> str | None:
    if (
        max_billable_tokens is not None
        and cumulative_billable_tokens >= max_billable_tokens
    ):
        return (
            f"max billable token cap reached: "
            f"{cumulative_billable_tokens:,} >= {max_billable_tokens:,}"
        )
    if (
        max_estimated_openai_cost_usd is not None
        and cumulative_estimated_cost >= max_estimated_openai_cost_usd
    ):
        return (
            f"max estimated OpenAI-equivalent cost reached: "
            f"${cumulative_estimated_cost:.6f} >= "
            f"${max_estimated_openai_cost_usd:.6f}"
        )
    return None


def record_missing_usage(record: BenchmarkRecord) -> bool:
    return record.ok and (record.input_tokens is None or record.output_tokens is None)


def run_single_request(
    *,
    client: httpx.Client,
    provider: ProviderConfig,
    model: str,
    prompt_item: PromptItem,
    prompt_index: int,
    run_index: int,
    max_output_tokens: int,
    reasoning_effort: str | None,
    timeout_seconds: float,
    input_price_per_mtok: float | None,
    output_price_per_mtok: float | None,
) -> BenchmarkRecord:
    record = run_once(
        client=client,
        provider=provider,
        model=model,
        prompt_item=prompt_item,
        prompt_index=prompt_index,
        run_index=run_index,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
        timeout_seconds=timeout_seconds,
    )
    return with_estimated_cost(
        record=record,
        input_price_per_mtok=input_price_per_mtok,
        output_price_per_mtok=output_price_per_mtok,
    )


def main() -> int:
    args = parse_args()
    load_environment()
    try:
        dataset_label, prompt_items = load_prompt_items(args)
    except (httpx.HTTPError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: unable to load prompts: {exc}", file=sys.stderr)
        return 2
    if not prompt_items:
        print("error: no prompts loaded", file=sys.stderr)
        return 2

    providers = args.provider or ["bedrock"]
    records: list[BenchmarkRecord] = []
    cumulative_billable_tokens = 0
    cumulative_estimated_cost = 0.0
    consecutive_missing_usage = 0
    stopped_reason: str | None = None
    args.output_dir.mkdir(parents=True, exist_ok=True)
    partial_stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    partial_jsonl_path = (
        args.output_dir / f"openai_responses_latency_{partial_stamp}_partial.jsonl"
    )
    max_concurrency = max(1, args.concurrency)
    limits = httpx.Limits(
        max_connections=max_concurrency,
        max_keepalive_connections=max_concurrency,
    )
    with httpx.Client(limits=limits) as client:
        for provider_name in providers:
            try:
                provider = provider_config(provider_name, args.region)
            except RuntimeError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
            if args.auth_debug:
                debug_auth(provider)
                return 0
            for model in models_for(provider_name, args.model):
                measured_prompt_items = (
                    prompt_items
                    if args.dataset or args.dataset_path
                    else [prompt_items[index % len(prompt_items)] for index in range(args.runs)]
                )
                warmup_prompt_items = [
                    prompt_items[index % len(prompt_items)] for index in range(args.warmups)
                ]
                total_runs = len(warmup_prompt_items) + len(measured_prompt_items)

                for index, prompt_item in enumerate(warmup_prompt_items):
                    prompt_index = index % len(prompt_items)
                    record = run_single_request(
                        client=client,
                        provider=provider,
                        model=model,
                        prompt_item=prompt_item,
                        prompt_index=prompt_index,
                        run_index=index + 1,
                        max_output_tokens=args.max_output_tokens,
                        reasoning_effort=args.reasoning_effort,
                        timeout_seconds=args.timeout_seconds,
                        input_price_per_mtok=args.input_price_per_mtok,
                        output_price_per_mtok=args.output_price_per_mtok,
                    )
                    cumulative_billable_tokens, cumulative_estimated_cost = (
                        update_cumulative_usage(
                            record=record,
                            cumulative_billable_tokens=cumulative_billable_tokens,
                            cumulative_estimated_cost=cumulative_estimated_cost,
                        )
                    )
                    print(
                        run_status_line(
                            record=record,
                            index=index + 1,
                            total_runs=total_runs,
                            cumulative_billable_tokens=cumulative_billable_tokens,
                            cumulative_estimated_cost=cumulative_estimated_cost,
                        ),
                        flush=True,
                    )
                    stopped_reason = cap_stop_reason(
                        cumulative_billable_tokens=cumulative_billable_tokens,
                        cumulative_estimated_cost=cumulative_estimated_cost,
                        max_billable_tokens=args.max_billable_tokens,
                        max_estimated_openai_cost_usd=args.max_estimated_openai_cost_usd,
                    )
                    if stopped_reason:
                        print(f"stopping: {stopped_reason}", file=sys.stderr)
                        break
                if stopped_reason:
                    break

                if max_concurrency == 1:
                    measured_records_iter: Iterable[BenchmarkRecord] = (
                        run_single_request(
                            client=client,
                            provider=provider,
                            model=model,
                            prompt_item=prompt_item,
                            prompt_index=index % len(prompt_items),
                            run_index=args.warmups + index + 1,
                            max_output_tokens=args.max_output_tokens,
                            reasoning_effort=args.reasoning_effort,
                            timeout_seconds=args.timeout_seconds,
                            input_price_per_mtok=args.input_price_per_mtok,
                            output_price_per_mtok=args.output_price_per_mtok,
                        )
                        for index, prompt_item in enumerate(measured_prompt_items)
                    )
                    for record in measured_records_iter:
                        cumulative_billable_tokens, cumulative_estimated_cost = (
                            update_cumulative_usage(
                                record=record,
                                cumulative_billable_tokens=cumulative_billable_tokens,
                                cumulative_estimated_cost=cumulative_estimated_cost,
                            )
                        )
                        records.append(record)
                        write_partial_record(partial_jsonl_path, record)
                        print(
                            run_status_line(
                                record=record,
                                index=record.run_index,
                                total_runs=total_runs,
                                cumulative_billable_tokens=cumulative_billable_tokens,
                                cumulative_estimated_cost=cumulative_estimated_cost,
                            ),
                            flush=True,
                        )
                        if record_missing_usage(record):
                            consecutive_missing_usage += 1
                        else:
                            consecutive_missing_usage = 0
                        if (
                            args.max_consecutive_missing_usage
                            and consecutive_missing_usage
                            >= args.max_consecutive_missing_usage
                        ):
                            stopped_reason = (
                                "missing token usage for "
                                f"{consecutive_missing_usage} consecutive OK responses"
                            )
                            print(f"stopping: {stopped_reason}", file=sys.stderr)
                            break
                        stopped_reason = cap_stop_reason(
                            cumulative_billable_tokens=cumulative_billable_tokens,
                            cumulative_estimated_cost=cumulative_estimated_cost,
                            max_billable_tokens=args.max_billable_tokens,
                            max_estimated_openai_cost_usd=args.max_estimated_openai_cost_usd,
                        )
                        if stopped_reason:
                            print(f"stopping: {stopped_reason}", file=sys.stderr)
                            break
                else:
                    next_index = 0
                    pending: dict[Future[BenchmarkRecord], int] = {}

                    def submit_next(executor: ThreadPoolExecutor) -> None:
                        nonlocal next_index
                        prompt_item = measured_prompt_items[next_index]
                        future = executor.submit(
                            run_single_request,
                            client=client,
                            provider=provider,
                            model=model,
                            prompt_item=prompt_item,
                            prompt_index=next_index % len(prompt_items),
                            run_index=args.warmups + next_index + 1,
                            max_output_tokens=args.max_output_tokens,
                            reasoning_effort=args.reasoning_effort,
                            timeout_seconds=args.timeout_seconds,
                            input_price_per_mtok=args.input_price_per_mtok,
                            output_price_per_mtok=args.output_price_per_mtok,
                        )
                        pending[future] = args.warmups + next_index + 1
                        next_index += 1

                    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
                        for _ in range(min(max_concurrency, len(measured_prompt_items))):
                            submit_next(executor)

                        while pending:
                            done, _ = wait(pending, return_when=FIRST_COMPLETED)
                            for future in done:
                                pending.pop(future)
                                record = future.result()
                                cumulative_billable_tokens, cumulative_estimated_cost = (
                                    update_cumulative_usage(
                                        record=record,
                                        cumulative_billable_tokens=cumulative_billable_tokens,
                                        cumulative_estimated_cost=cumulative_estimated_cost,
                                    )
                                )
                                records.append(record)
                                write_partial_record(partial_jsonl_path, record)
                                print(
                                    run_status_line(
                                        record=record,
                                        index=record.run_index,
                                        total_runs=total_runs,
                                        cumulative_billable_tokens=cumulative_billable_tokens,
                                        cumulative_estimated_cost=cumulative_estimated_cost,
                                    ),
                                    flush=True,
                                )
                                if record_missing_usage(record):
                                    consecutive_missing_usage += 1
                                else:
                                    consecutive_missing_usage = 0
                                if (
                                    args.max_consecutive_missing_usage
                                    and consecutive_missing_usage
                                    >= args.max_consecutive_missing_usage
                                ):
                                    stopped_reason = (
                                        "missing token usage for "
                                        f"{consecutive_missing_usage} consecutive OK responses"
                                    )
                                    print(f"stopping: {stopped_reason}", file=sys.stderr)
                                    for queued in pending:
                                        queued.cancel()
                                    break
                                stopped_reason = cap_stop_reason(
                                    cumulative_billable_tokens=cumulative_billable_tokens,
                                    cumulative_estimated_cost=cumulative_estimated_cost,
                                    max_billable_tokens=args.max_billable_tokens,
                                    max_estimated_openai_cost_usd=args.max_estimated_openai_cost_usd,
                                )
                                if stopped_reason:
                                    print(f"stopping: {stopped_reason}", file=sys.stderr)
                                    for queued in pending:
                                        queued.cancel()
                                    break
                                if next_index < len(measured_prompt_items):
                                    submit_next(executor)
                            if stopped_reason:
                                break
                if stopped_reason:
                    break
            if stopped_reason:
                break

    records.sort(key=lambda record: (record.provider, record.model, record.run_index))
    summary_rows = summarize(records)
    aggregate_rows = aggregate_metrics(records)
    jsonl_path, summary_json_path, md_path = write_outputs(
        records=records,
        summary_rows=summary_rows,
        aggregate_rows=aggregate_rows,
        dataset_label=dataset_label,
        output_dir=args.output_dir,
        region=args.region,
        warmups=args.warmups,
        measured_runs=len(prompt_items) if (args.dataset or args.dataset_path) else args.runs,
        max_output_tokens=args.max_output_tokens,
        reasoning_effort=args.reasoning_effort,
    )
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {summary_json_path}")
    print(f"Wrote {md_path}")
    print(markdown_summary(
        records=records,
        summary=summary_rows,
        aggregates=aggregate_rows,
        dataset_label=dataset_label,
        region=args.region,
        warmups=args.warmups,
        measured_runs=len(prompt_items) if (args.dataset or args.dataset_path) else args.runs,
        max_output_tokens=args.max_output_tokens,
        reasoning_effort=args.reasoning_effort,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
