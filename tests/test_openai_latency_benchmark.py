from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_openai_latency.py"
SPEC = importlib.util.spec_from_file_location("benchmark_openai_latency", SCRIPT_PATH)
assert SPEC is not None
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)


def test_percentile_uses_nearest_rank() -> None:
    values = [500.0, 100.0, 300.0, 200.0, 400.0]

    assert benchmark.percentile(values, 50) == 300.0
    assert benchmark.percentile(values, 90) == 500.0


def test_summarize_ignores_failed_records() -> None:
    records = [
        benchmark.BenchmarkRecord(
            provider="bedrock",
            model="openai.gpt-5.4",
            run_index=1,
            prompt_index=0,
            started_at="2026-06-08T12:00:00+00:00",
            ok=True,
            ttfb_ms=100.0,
            ttft_ms=250.0,
            total_ms=1_000.0,
            input_tokens=50,
            output_tokens=150,
            reasoning_tokens=80,
            output_tokens_per_second=20.0,
            estimated_openai_cost_usd=0.002375,
        ),
        benchmark.BenchmarkRecord(
            provider="bedrock",
            model="openai.gpt-5.4",
            run_index=2,
            prompt_index=1,
            started_at="2026-06-08T12:01:00+00:00",
            ok=False,
            error="HTTP 429",
        ),
        benchmark.BenchmarkRecord(
            provider="bedrock",
            model="openai.gpt-5.4",
            run_index=3,
            prompt_index=2,
            started_at="2026-06-08T12:02:00+00:00",
            ok=True,
            ttfb_ms=200.0,
            ttft_ms=300.0,
            total_ms=1_200.0,
            input_tokens=60,
            output_tokens=170,
            reasoning_tokens=120,
            output_tokens_per_second=30.0,
            estimated_openai_cost_usd=0.0027,
        ),
    ]

    summary = benchmark.summarize(records)

    assert summary == [
        {
            "provider": "bedrock",
            "model": "openai.gpt-5.4",
            "successful_runs": 2,
            "failed_runs": 1,
            "ttfb_ms_avg": 150.0,
            "ttfb_ms_p50": 100.0,
            "ttfb_ms_p90": 200.0,
            "ttfb_ms_p95": 200.0,
            "ttft_ms_avg": 275.0,
            "ttft_ms_p50": 250.0,
            "ttft_ms_p90": 300.0,
            "ttft_ms_p95": 300.0,
            "total_ms_avg": 1_100.0,
            "total_ms_p50": 1_000.0,
            "total_ms_p90": 1_200.0,
            "total_ms_p95": 1_200.0,
            "input_tokens_avg": 55.0,
            "input_tokens_p50": 50,
            "input_tokens_p90": 60,
            "input_tokens_p95": 60,
            "output_tokens_avg": 160.0,
            "output_tokens_p50": 150,
            "output_tokens_p90": 170,
            "output_tokens_p95": 170,
            "reasoning_tokens_avg": 100.0,
            "reasoning_tokens_p50": 80,
            "reasoning_tokens_p90": 120,
            "reasoning_tokens_p95": 120,
            "output_tokens_per_second_avg": 25.0,
            "output_tokens_per_second_p50": 20.0,
            "output_tokens_per_second_p90": 30.0,
            "output_tokens_per_second_p95": 30.0,
            "estimated_openai_cost_usd_total": 0.005075,
        }
    ]


def test_markdown_summary_contains_latency_table() -> None:
    rows = [
        {
            "provider": "bedrock",
            "model": "openai.gpt-5.5",
            "successful_runs": 3,
            "failed_runs": 0,
            "ttfb_ms_p50": 110.0,
            "ttft_ms_p50": 900.0,
            "total_ms_p50": 2_400.0,
            "input_tokens_p50": 180,
            "output_tokens_p50": 1_400,
            "reasoning_tokens_p50": 1_024,
            "estimated_openai_cost_usd_total": 0.1275,
        }
    ]

    markdown = benchmark.markdown_summary(
        records=[],
        summary=rows,
        aggregates=[],
        dataset_label="default-prompts",
        region="us-east-2",
        warmups=1,
        measured_runs=3,
        max_output_tokens=180,
        reasoning_effort="medium",
    )

    assert "| bedrock | `openai.gpt-5.5` | 3 | 0 | 110 ms | 900 ms | 2,400 ms | 180 | 1,400 | 1,024 | $0.1275 |" in markdown
    assert "TTFB is measured from request start" in markdown


def test_load_jsonl_prompts_preserves_prompt_metadata(tmp_path: Path) -> None:
    dataset_path = tmp_path / "sample.jsonl"
    dataset_path.write_text(
        '{"question":"What is 2+2?","answer":"#### 4"}\n'
        '{"question":"What is 3+3?","answer":"#### 6"}\n',
        encoding="utf-8",
    )

    prompts = benchmark.load_jsonl_prompts(
        path=dataset_path,
        question_key="question",
        answer_key="answer",
        limit=1,
    )

    assert prompts == [
        benchmark.PromptItem(
            prompt_id="sample-0",
            prompt_text="What is 2+2?",
            expected_answer="#### 4",
        )
    ]


def test_aggregate_metrics_reports_llmperf_style_percentiles() -> None:
    records = [
        benchmark.BenchmarkRecord(
            provider="bedrock",
            model="openai.gpt-5.5",
            run_index=1,
            prompt_index=0,
            started_at="2026-06-08T12:00:00+00:00",
            ok=True,
            ttft_ms=200.0,
            total_ms=1_000.0,
            input_tokens=100,
            output_tokens=300,
            reasoning_tokens=128,
            output_tokens_per_second=30.0,
            estimated_openai_cost_usd=0.01,
        ),
        benchmark.BenchmarkRecord(
            provider="bedrock",
            model="openai.gpt-5.5",
            run_index=2,
            prompt_index=1,
            started_at="2026-06-08T12:01:00+00:00",
            ok=True,
            ttft_ms=400.0,
            total_ms=2_000.0,
            input_tokens=120,
            output_tokens=500,
            reasoning_tokens=256,
            output_tokens_per_second=40.0,
            estimated_openai_cost_usd=0.03,
        ),
        benchmark.BenchmarkRecord(
            provider="bedrock",
            model="openai.gpt-5.5",
            run_index=3,
            prompt_index=2,
            started_at="2026-06-08T12:02:00+00:00",
            ok=False,
            error="HTTP 429",
        ),
    ]

    aggregates = benchmark.aggregate_metrics(records)

    assert aggregates[0]["number_completed_requests"] == 2
    assert aggregates[0]["number_errored_requests"] == 1
    assert aggregates[0]["estimated_openai_cost_usd_total"] == 0.04
    assert aggregates[0]["estimated_openai_cost_usd_mean"] == 0.02
    assert aggregates[0]["metrics"]["time_to_first_token_ms"]["p50"] == 200.0
    assert aggregates[0]["metrics"]["time_to_first_token_ms"]["p90"] == 400.0
    assert aggregates[0]["metrics"]["end_to_end_latency_ms"]["p95"] == 2_000.0
    assert aggregates[0]["metrics"]["number_output_tokens"]["mean"] == 400.0
    assert aggregates[0]["metrics"]["estimated_openai_cost_usd"]["p95"] == 0.03


def test_estimate_openai_cost_uses_bedrock_model_alias() -> None:
    record = benchmark.BenchmarkRecord(
        provider="bedrock",
        model="openai.gpt-5.4",
        run_index=1,
        prompt_index=0,
        started_at="2026-06-08T12:00:00+00:00",
        ok=True,
        input_tokens=1_000,
        output_tokens=2_000,
    )

    assert (
        benchmark.estimate_openai_cost(
            record=record,
            input_price_per_mtok=None,
            output_price_per_mtok=None,
        )
        == 0.0325
    )


def test_extract_stream_error_from_response_failed_event() -> None:
    event = {
        "type": "response.failed",
        "response": {
            "status": "failed",
            "error": {
                "code": "insufficient_quota",
                "message": "You exceeded your current quota.",
            },
        },
    }

    assert (
        benchmark.extract_stream_error(event)
        == "insufficient_quota: You exceeded your current quota."
    )
