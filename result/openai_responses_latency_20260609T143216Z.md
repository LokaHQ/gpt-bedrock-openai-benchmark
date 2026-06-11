# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-09T14:32:16+00:00`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `5`
Prompt variants: `3`
Max output tokens: `512`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bedrock | `openai.gpt-5.5` | 5 | 0 | 241 ms | 828 ms | 1,705 ms | 204 | 100 | 21 | $0.0197 |

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
