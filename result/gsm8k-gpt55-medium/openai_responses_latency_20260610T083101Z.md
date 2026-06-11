# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-10T08:31:01+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `1024`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bedrock | `openai.gpt-5.5` | 1319 | 0 | 220 ms | 1,939 ms | 2,881 ms | 116 | 114 | 50 | $5.8652 |

## LLMPerf-style aggregate metrics

### bedrock `openai.gpt-5.5`

Completed requests: `1319`
Errored requests: `0`
Overall output throughput: `43.23` tokens/s
Completed requests per minute: `20.22`
Estimated OpenAI-equivalent cost total: `$5.8652`
Estimated OpenAI-equivalent cost mean/request: `$0.0044`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 219.96 | 306.78 | 355.57 | 241.02 | 179.42 | 1,255.02 | 66.23 |
| time_to_first_token_ms | 1,939.48 | 3,782.45 | 4,363.70 | 2,377.03 | 740.41 | 19,201.30 | 1,524.67 |
| end_to_end_latency_ms | 2,880.85 | 4,368.89 | 4,976.11 | 2,968.44 | 975.44 | 20,022.14 | 1,641.38 |
| request_output_throughput_token_per_s | 44.75 | 71.92 | 77.83 | 47.36 | 14.64 | 101.60 | 17.58 |
| number_input_tokens | 116.00 | 149.00 | 162.00 | 119.46 | 83.00 | 245.00 | 21.55 |
| number_output_tokens | 114.00 | 187.00 | 234.00 | 128.31 | 38.00 | 832.00 | 74.75 |
| number_reasoning_tokens | 50.00 | 101.00 | 142.00 | 62.55 | 9.00 | 737.00 | 67.04 |
| estimated_openai_cost_usd | 0.00 | 0.01 | 0.01 | 0.00 | 0.00 | 0.03 | 0.00 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
