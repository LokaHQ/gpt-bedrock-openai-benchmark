# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T13:55:49+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `1`
Max output tokens: `256`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 0 | 1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `0`
Errored requests: `1`
Overall output throughput: `n/a` tokens/s
Completed requests per minute: `n/a`
Estimated OpenAI-equivalent cost total: `n/a`
Estimated OpenAI-equivalent cost mean/request: `n/a`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| time_to_first_token_ms | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| end_to_end_latency_ms | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| request_output_throughput_token_per_s | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_input_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_output_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_reasoning_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| estimated_openai_cost_usd | n/a | n/a | n/a | n/a | n/a | n/a | n/a |


## Failures

- `openai` `gpt-5.5` run 1: insufficient_quota: You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
