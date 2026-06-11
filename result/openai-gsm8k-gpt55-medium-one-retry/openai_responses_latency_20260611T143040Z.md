# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T14:30:40+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `1`
Max output tokens: `256`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1 | 0 | 1,499 ms | 3,148 ms | 4,619 ms | 124 | 97 | 39 | $0.0035 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1`
Errored requests: `0`
Overall output throughput: `21.00` tokens/s
Completed requests per minute: `n/a`
Estimated OpenAI-equivalent cost total: `$0.0035`
Estimated OpenAI-equivalent cost mean/request: `$0.0035`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 1,498.61 | 1,498.61 | 1,498.61 | 1,498.61 | 1,498.61 | 1,498.61 | n/a |
| time_to_first_token_ms | 3,147.77 | 3,147.77 | 3,147.77 | 3,147.77 | 3,147.77 | 3,147.77 | n/a |
| end_to_end_latency_ms | 4,618.88 | 4,618.88 | 4,618.88 | 4,618.88 | 4,618.88 | 4,618.88 | n/a |
| request_output_throughput_token_per_s | 21.00 | 21.00 | 21.00 | 21.00 | 21.00 | 21.00 | n/a |
| number_input_tokens | 124.00 | 124.00 | 124.00 | 124.00 | 124.00 | 124.00 | n/a |
| number_output_tokens | 97.00 | 97.00 | 97.00 | 97.00 | 97.00 | 97.00 | n/a |
| number_reasoning_tokens | 39.00 | 39.00 | 39.00 | 39.00 | 39.00 | 39.00 | n/a |
| estimated_openai_cost_usd | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | n/a |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
