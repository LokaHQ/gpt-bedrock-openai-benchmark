# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T10:06:29+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `1`
Max output tokens: `256`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1 | 0 | 1,678 ms | 2,487 ms | 3,698 ms | 124 | 81 | 13 | $0.0031 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1`
Errored requests: `0`
Overall output throughput: `21.90` tokens/s
Completed requests per minute: `n/a`
Estimated OpenAI-equivalent cost total: `$0.0031`
Estimated OpenAI-equivalent cost mean/request: `$0.0031`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 1,677.77 | 1,677.77 | 1,677.77 | 1,677.77 | 1,677.77 | 1,677.77 | n/a |
| time_to_first_token_ms | 2,487.16 | 2,487.16 | 2,487.16 | 2,487.16 | 2,487.16 | 2,487.16 | n/a |
| end_to_end_latency_ms | 3,698.50 | 3,698.50 | 3,698.50 | 3,698.50 | 3,698.50 | 3,698.50 | n/a |
| request_output_throughput_token_per_s | 21.90 | 21.90 | 21.90 | 21.90 | 21.90 | 21.90 | n/a |
| number_input_tokens | 124.00 | 124.00 | 124.00 | 124.00 | 124.00 | 124.00 | n/a |
| number_output_tokens | 81.00 | 81.00 | 81.00 | 81.00 | 81.00 | 81.00 | n/a |
| number_reasoning_tokens | 13.00 | 13.00 | 13.00 | 13.00 | 13.00 | 13.00 | n/a |
| estimated_openai_cost_usd | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | n/a |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
