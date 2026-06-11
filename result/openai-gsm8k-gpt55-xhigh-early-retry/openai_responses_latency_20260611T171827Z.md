# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T17:18:27+00:00`
Dataset: `result/openai-gsm8k-gpt55-xhigh-error-fixed/xhigh_early_failures_retry_dataset.jsonl`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `2`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 2 | 0 | 679 ms | 3,617 ms | 3,930 ms | 34 | 100 | 75 | $0.0078 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `2`
Errored requests: `0`
Overall output throughput: `28.89` tokens/s
Completed requests per minute: `30.53`
Estimated OpenAI-equivalent cost total: `$0.0078`
Estimated OpenAI-equivalent cost mean/request: `$0.0039`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 678.73 | 1,329.82 | 1,329.82 | 1,004.27 | 678.73 | 1,329.82 | 460.39 |
| time_to_first_token_ms | 3,616.79 | 4,636.36 | 4,636.36 | 4,126.57 | 3,616.79 | 4,636.36 | 720.94 |
| end_to_end_latency_ms | 3,930.04 | 4,724.87 | 4,724.87 | 4,327.45 | 3,930.04 | 4,724.87 | 562.03 |
| request_output_throughput_token_per_s | 25.45 | 31.75 | 31.75 | 28.60 | 25.45 | 31.75 | 4.45 |
| number_input_tokens | 34.00 | 34.00 | 34.00 | 34.00 | 34.00 | 34.00 | 0.00 |
| number_output_tokens | 100.00 | 150.00 | 150.00 | 125.00 | 100.00 | 150.00 | 35.36 |
| number_reasoning_tokens | 75.00 | 140.00 | 140.00 | 107.50 | 75.00 | 140.00 | 45.96 |
| estimated_openai_cost_usd | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
