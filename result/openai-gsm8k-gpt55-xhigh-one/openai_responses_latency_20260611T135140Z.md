# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T13:51:40+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `1`
Max output tokens: `512`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1 | 0 | 1,898 ms | n/a | 1,914 ms | n/a | n/a | n/a | n/a |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1`
Errored requests: `0`
Overall output throughput: `0.00` tokens/s
Completed requests per minute: `n/a`
Estimated OpenAI-equivalent cost total: `n/a`
Estimated OpenAI-equivalent cost mean/request: `n/a`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 1,897.86 | 1,897.86 | 1,897.86 | 1,897.86 | 1,897.86 | 1,897.86 | n/a |
| time_to_first_token_ms | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| end_to_end_latency_ms | 1,914.37 | 1,914.37 | 1,914.37 | 1,914.37 | 1,914.37 | 1,914.37 | n/a |
| request_output_throughput_token_per_s | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_input_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_output_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_reasoning_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| estimated_openai_cost_usd | n/a | n/a | n/a | n/a | n/a | n/a | n/a |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
