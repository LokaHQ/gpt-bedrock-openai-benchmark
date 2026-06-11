# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T17:16:30+00:00`
Dataset: `result/openai-gsm8k-gpt55-xhigh-error-fixed/xhigh_failed_tail_retry_dataset.jsonl`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `182`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 182 | 0 | 529 ms | 3,185 ms | 4,408 ms | 116 | 168 | 100 | $1.2671 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `182`
Errored requests: `0`
Overall output throughput: `39.34` tokens/s
Completed requests per minute: `11.18`
Estimated OpenAI-equivalent cost total: `$1.2671`
Estimated OpenAI-equivalent cost mean/request: `$0.0070`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 529.08 | 875.89 | 1,048.80 | 587.82 | 347.87 | 1,310.77 | 205.21 |
| time_to_first_token_ms | 3,184.64 | 5,697.11 | 6,755.97 | 3,957.45 | 1,466.58 | 45,225.49 | 3,762.80 |
| end_to_end_latency_ms | 4,407.79 | 7,475.13 | 9,234.35 | 5,385.75 | 2,359.73 | 64,637.51 | 5,129.81 |
| request_output_throughput_token_per_s | 40.41 | 52.88 | 53.84 | 40.00 | 9.08 | 62.59 | 9.82 |
| number_input_tokens | 116.00 | 155.00 | 171.00 | 121.18 | 86.00 | 220.00 | 24.85 |
| number_output_tokens | 168.00 | 317.00 | 390.00 | 211.87 | 84.00 | 2,721.00 | 219.12 |
| number_reasoning_tokens | 100.00 | 222.00 | 296.00 | 145.20 | 27.00 | 2,588.00 | 210.36 |
| estimated_openai_cost_usd | 0.01 | 0.01 | 0.01 | 0.01 | 0.00 | 0.08 | 0.01 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
