# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-10T08:36:24+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `0`
Measured runs per model: `2`
Max output tokens: `180`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
