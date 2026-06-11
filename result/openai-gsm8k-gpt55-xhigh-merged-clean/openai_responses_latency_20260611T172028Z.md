# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T17:20:28+00:00`
Dataset: `gsm8k test; original xhigh with failed requests retried`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1319 | 0 | 502 ms | 3,280 ms | 4,334 ms | 116 | 168 | 103 | $9.5409 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1319`
Errored requests: `0`
Overall output throughput: `37.28` tokens/s
Completed requests per minute: `7.95`
Estimated OpenAI-equivalent cost total: `$9.5409`
Estimated OpenAI-equivalent cost mean/request: `$0.0072`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 502.32 | 897.31 | 1,288.96 | 856.15 | 329.73 | 149,901.29 | 4,900.46 |
| time_to_first_token_ms | 3,279.85 | 6,755.97 | 9,336.03 | 4,703.12 | 1,384.06 | 190,512.03 | 8,449.31 |
| end_to_end_latency_ms | 4,333.66 | 8,273.25 | 11,446.55 | 5,933.27 | 1,907.50 | 190,562.75 | 9,049.67 |
| request_output_throughput_token_per_s | 40.19 | 51.66 | 54.21 | 39.72 | 0.73 | 66.71 | 9.51 |
| number_input_tokens | 116.00 | 149.00 | 162.00 | 119.64 | 83.00 | 356.00 | 22.51 |
| number_output_tokens | 168.00 | 325.00 | 472.00 | 221.18 | 68.00 | 4,096.00 | 262.07 |
| number_reasoning_tokens | 103.00 | 249.00 | 386.00 | 156.89 | 27.00 | 4,096.00 | 259.13 |
| estimated_openai_cost_usd | 0.01 | 0.01 | 0.01 | 0.01 | 0.00 | 0.12 | 0.01 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
