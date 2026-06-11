# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-10T07:15:20+00:00`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `5`
Prompt variants: `3`
Max output tokens: `512`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bedrock | `openai.gpt-5.5` | 5 | 0 | 300 ms | 1,324 ms | 3,433 ms | 53 | 93 | 18 | $0.0161 |

## LLMPerf-style aggregate metrics

### bedrock `openai.gpt-5.5`

Completed requests: `5`
Errored requests: `0`
Overall output throughput: `30.23` tokens/s
Completed requests per minute: `23.36`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 300.46 | 373.35 | 373.35 | 311.74 | 281.32 | 373.35 | 35.98 |
| time_to_first_token_ms | 1,324.39 | 2,645.04 | 2,645.04 | 1,571.37 | 1,020.37 | 2,645.04 | 657.98 |
| end_to_end_latency_ms | 3,433.24 | 3,733.22 | 3,733.22 | 3,254.78 | 2,658.52 | 3,733.22 | 429.25 |
| request_output_throughput_token_per_s | 24.91 | 43.28 | 43.28 | 31.17 | 23.07 | 43.28 | 10.07 |
| number_input_tokens | 53.00 | 56.00 | 56.00 | 53.40 | 49.00 | 56.00 | 2.88 |
| number_output_tokens | 93.00 | 129.00 | 129.00 | 98.40 | 80.00 | 129.00 | 20.73 |
| number_reasoning_tokens | 18.00 | 26.00 | 26.00 | 17.00 | 0.00 | 26.00 | 10.10 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
