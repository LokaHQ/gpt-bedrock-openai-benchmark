# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-10T09:57:51+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `2048`
Reasoning effort: `high`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bedrock | `openai.gpt-5.5` | 1319 | 0 | 224 ms | 2,662 ms | 3,455 ms | 116 | 134 | 70 | $7.0816 |

## LLMPerf-style aggregate metrics

### bedrock `openai.gpt-5.5`

Completed requests: `1319`
Errored requests: `0`
Overall output throughput: `45.49` tokens/s
Completed requests per minute: `17.16`
Estimated OpenAI-equivalent cost total: `$7.0816`
Estimated OpenAI-equivalent cost mean/request: `$0.0054`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 223.99 | 299.10 | 337.61 | 239.74 | 173.75 | 1,597.70 | 71.57 |
| time_to_first_token_ms | 2,662.03 | 4,161.29 | 5,157.15 | 2,902.14 | 746.38 | 30,676.00 | 2,187.40 |
| end_to_end_latency_ms | 3,455.46 | 4,800.74 | 5,987.40 | 3,496.78 | 1,043.40 | 44,749.45 | 2,538.54 |
| request_output_throughput_token_per_s | 45.13 | 72.75 | 79.38 | 48.49 | 12.70 | 103.84 | 16.81 |
| number_input_tokens | 116.00 | 149.00 | 162.00 | 119.46 | 83.00 | 245.00 | 21.55 |
| number_output_tokens | 134.00 | 226.00 | 303.00 | 159.05 | 46.00 | 2,048.00 | 126.39 |
| number_reasoning_tokens | 70.00 | 143.00 | 214.00 | 94.49 | 14.00 | 2,048.00 | 121.69 |
| estimated_openai_cost_usd | 0.00 | 0.01 | 0.01 | 0.01 | 0.00 | 0.06 | 0.00 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
