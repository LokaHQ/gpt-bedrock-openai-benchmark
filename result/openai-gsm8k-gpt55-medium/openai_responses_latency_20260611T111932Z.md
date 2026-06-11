# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T11:19:32+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `1024`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1317 | 2 | 484 ms | 1,956 ms | 2,859 ms | 116 | 112 | 48 | $5.7201 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1317`
Errored requests: `2`
Overall output throughput: `37.91` tokens/s
Completed requests per minute: `18.14`
Estimated OpenAI-equivalent cost total: `$5.7201`
Estimated OpenAI-equivalent cost mean/request: `$0.0043`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 484.20 | 822.20 | 1,149.27 | 614.72 | 321.80 | 17,365.19 | 718.39 |
| time_to_first_token_ms | 1,955.73 | 3,508.57 | 4,440.46 | 2,300.31 | 924.94 | 18,820.98 | 1,412.07 |
| end_to_end_latency_ms | 2,858.67 | 4,907.71 | 5,965.45 | 3,293.96 | 1,374.30 | 21,652.15 | 1,789.46 |
| request_output_throughput_token_per_s | 39.69 | 50.90 | 53.10 | 39.07 | 3.98 | 66.17 | 9.57 |
| number_input_tokens | 116.00 | 149.00 | 162.00 | 119.46 | 83.00 | 245.00 | 21.56 |
| number_output_tokens | 112.00 | 184.00 | 229.00 | 124.98 | 41.00 | 767.00 | 67.89 |
| number_reasoning_tokens | 48.00 | 100.00 | 137.00 | 60.03 | 9.00 | 682.00 | 60.36 |
| estimated_openai_cost_usd | 0.00 | 0.01 | 0.01 | 0.00 | 0.00 | 0.02 | 0.00 |


## Failures

- `openai` `gpt-5.5` run 326: HTTP 503: upstream connect error or disconnect/reset before headers. reset reason: connection timeout
- `openai` `gpt-5.5` run 750: HTTP 503: upstream connect error or disconnect/reset before headers. reset reason: connection timeout

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
