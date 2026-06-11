# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-10T12:00:08+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bedrock | `openai.gpt-5.5` | 1319 | 0 | 223 ms | 3,250 ms | 3,803 ms | 116 | 164 | 99 | $9.2775 |

## LLMPerf-style aggregate metrics

### bedrock `openai.gpt-5.5`

Completed requests: `1319`
Errored requests: `0`
Overall output throughput: `49.35` tokens/s
Completed requests per minute: `13.80`
Estimated OpenAI-equivalent cost total: `$9.2775`
Estimated OpenAI-equivalent cost mean/request: `$0.0070`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 222.95 | 300.23 | 349.92 | 238.92 | 176.23 | 1,046.19 | 65.22 |
| time_to_first_token_ms | 3,249.58 | 4,949.48 | 7,472.88 | 3,569.08 | 945.14 | 42,706.82 | 3,272.99 |
| end_to_end_latency_ms | 3,803.45 | 5,791.94 | 9,150.53 | 4,347.55 | 1,075.82 | 83,940.88 | 4,991.26 |
| request_output_throughput_token_per_s | 48.61 | 75.64 | 81.59 | 51.76 | 18.47 | 108.35 | 16.09 |
| number_input_tokens | 116.00 | 149.00 | 162.00 | 119.46 | 83.00 | 245.00 | 21.55 |
| number_output_tokens | 164.00 | 297.00 | 447.00 | 214.55 | 65.00 | 4,096.00 | 257.24 |
| number_reasoning_tokens | 99.00 | 221.00 | 362.00 | 150.07 | 23.00 | 4,096.00 | 256.35 |
| estimated_openai_cost_usd | 0.01 | 0.01 | 0.01 | 0.01 | 0.00 | 0.12 | 0.01 |


## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
