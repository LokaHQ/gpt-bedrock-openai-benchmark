# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T13:34:00+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 3 | 0 | 606 ms | n/a | 608 ms | n/a | n/a | n/a | n/a |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `3`
Errored requests: `0`
Overall output throughput: `0.00` tokens/s
Completed requests per minute: `132.66`
Estimated OpenAI-equivalent cost total: `n/a`
Estimated OpenAI-equivalent cost mean/request: `n/a`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 606.48 | 839.46 | 839.46 | 654.06 | 516.23 | 839.46 | 166.78 |
| time_to_first_token_ms | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| end_to_end_latency_ms | 608.28 | 839.83 | 839.83 | 654.84 | 516.40 | 839.83 | 166.67 |
| request_output_throughput_token_per_s | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_input_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_output_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| number_reasoning_tokens | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| estimated_openai_cost_usd | n/a | n/a | n/a | n/a | n/a | n/a | n/a |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
