# GPT-5.5 Bedrock Mantle vs OpenAI Benchmark

This repo contains the standalone benchmark scripts and saved GSM8K results used to compare OpenAI-compatible `gpt-5.5` responses through:

- Amazon Bedrock Mantle in `us-east-2`
- OpenAI API

The benchmark records streaming latency, token usage, reasoning tokens, output throughput, failures, and estimated OpenAI-equivalent cost.

## Setup

```bash
uv sync
```

For OpenAI runs, create a local `.env` with `OPENAI_API_KEY`. Do not commit it.

For Bedrock runs, use an AWS profile with Bedrock Mantle and Marketplace subscription permissions:

```bash
AWS_PROFILE=Loka-ml uv run python scripts/benchmark_openai_latency.py ...
```

## Main Benchmark Command

Bedrock example:

```bash
AWS_PROFILE=Loka-ml uv run python scripts/benchmark_openai_latency.py \
  --provider bedrock \
  --region us-east-2 \
  --model openai.gpt-5.5 \
  --dataset gsm8k \
  --split test \
  --warmups 1 \
  --reasoning-effort medium \
  --max-output-tokens 4096 \
  --concurrency 1 \
  --timeout-seconds 240 \
  --max-billable-tokens 750000 \
  --max-estimated-openai-cost-usd 10.00 \
  --output-dir result/gsm8k-gpt55-medium
```

OpenAI example:

```bash
uv run python scripts/benchmark_openai_latency.py \
  --provider openai \
  --model gpt-5.5 \
  --dataset gsm8k \
  --split test \
  --warmups 1 \
  --reasoning-effort medium \
  --max-output-tokens 4096 \
  --concurrency 1 \
  --timeout-seconds 240 \
  --max-billable-tokens 750000 \
  --max-estimated-openai-cost-usd 10.00 \
  --output-dir result/openai-gsm8k-gpt55-medium
```

Change `--reasoning-effort` to `medium`, `high`, or `xhigh`.

## Accuracy Scoring

Generate offline GSM8K accuracy summaries from the saved benchmark JSONL artifacts:

```bash
uv run python scripts/score_gsm8k_accuracy.py --main-runs
```

The scorer uses the original GSM8K `test.jsonl` answers, extracts the final `####` answer from both the dataset reference and the saved model response, normalizes the final answer, and compares them.

## Final Result Folders

Bedrock:

- `result/gsm8k-gpt55-medium`
- `result/gsm8k-gpt55-high`
- `result/gsm8k-gpt55-xhigh`

OpenAI:

- `result/openai-gsm8k-gpt55-medium`
- `result/openai-gsm8k-gpt55-high`
- `result/openai-gsm8k-gpt55-xhigh-merged-clean`

The OpenAI `xhigh` result is a merged clean result: the original run had a local network interruption near the end, and the failed prompts were retried and merged back into a `1319 / 0` successful result.

Each main result folder now also contains:

- `gsm8k_accuracy_summary.json`
- `gsm8k_accuracy_summary.md`

Aggregate accuracy comparison files for the six main runs are written to:

- `result/gsm8k_accuracy_main_runs.json`
- `result/gsm8k_accuracy_main_runs.md`

## Current Summary

| Effort | Provider | OK / Failed | Accuracy | Cost | TTFB p50 | TTFT p50 | TTFT p90 | Total p50 | Total p90 | Total p95 | Output tok/s p50 | RPM |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Medium | Bedrock | 1319 / 0 | 97.57% | $5.865 | 220 ms | 1.939s | 3.782s | 2.881s | 4.369s | 4.976s | 44.75 | 20.22 |
| Medium | OpenAI | 1317 / 2 | 97.42% | $5.720 | 484 ms | 1.956s | 3.509s | 2.859s | 4.908s | 5.965s | 39.69 | 18.14 |
| High | Bedrock | 1319 / 0 | 97.57% | $7.082 | 224 ms | 2.662s | 4.161s | 3.455s | 4.801s | 5.987s | 45.13 | 17.16 |
| High | OpenAI | 1318 / 1 | 97.35% | $6.899 | 497 ms | 2.356s | 4.280s | 3.248s | 5.712s | 6.971s | 42.32 | 15.03 |
| xHigh | Bedrock | 1319 / 0 | 97.42% | $9.278 | 223 ms | 3.250s | 4.949s | 3.803s | 5.792s | 9.151s | 48.61 | 13.80 |
| xHigh | OpenAI | 1319 / 0 | 97.35% | $9.541 | 502 ms | 3.280s | 6.756s | 4.334s | 8.273s | 11.447s | 40.19 | 7.95 |

## Notes

- TTFB measures request start to first non-empty streamed line.
- TTFT measures request start to first streamed output-text delta.
- Total latency measures request start through stream completion.
- Reasoning tokens are billed as output tokens.
- Runs were sequential (`--concurrency 1`) to avoid conflating provider latency with client-side concurrency effects.
- Accuracy is scored offline from saved JSONL outputs by comparing the final `####` answer against the original GSM8K test-set answer after normalization.

## Validation

```bash
uv run ruff check scripts tests
uv run pytest
```
