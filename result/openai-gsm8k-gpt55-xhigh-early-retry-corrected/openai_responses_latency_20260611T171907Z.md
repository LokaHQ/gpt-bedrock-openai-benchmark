# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T17:19:07+00:00`
Dataset: `result/openai-gsm8k-gpt55-xhigh-error-fixed/xhigh_early_failures_retry_dataset_corrected.jsonl`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `2`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 2 | 0 | 666 ms | 2,949 ms | 3,377 ms | 93 | 132 | 86 | $0.0125 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `2`
Errored requests: `0`
Overall output throughput: `44.13` tokens/s
Completed requests per minute: `35.53`
Estimated OpenAI-equivalent cost total: `$0.0125`
Estimated OpenAI-equivalent cost mean/request: `$0.0062`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 666.38 | 782.73 | 782.73 | 724.56 | 666.38 | 782.73 | 82.27 |
| time_to_first_token_ms | 2,948.54 | 3,787.16 | 3,787.16 | 3,367.85 | 2,948.54 | 3,787.16 | 592.99 |
| end_to_end_latency_ms | 3,376.78 | 5,143.39 | 5,143.39 | 4,260.09 | 3,376.78 | 5,143.39 | 1,249.18 |
| request_output_throughput_token_per_s | 39.09 | 47.44 | 47.44 | 43.27 | 39.09 | 47.44 | 5.90 |
| number_input_tokens | 93.00 | 150.00 | 150.00 | 121.50 | 93.00 | 150.00 | 40.31 |
| number_output_tokens | 132.00 | 244.00 | 244.00 | 188.00 | 132.00 | 244.00 | 79.20 |
| number_reasoning_tokens | 86.00 | 139.00 | 139.00 | 112.50 | 86.00 | 139.00 | 37.48 |
| estimated_openai_cost_usd | 0.00 | 0.01 | 0.01 | 0.01 | 0.00 | 0.01 | 0.00 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
