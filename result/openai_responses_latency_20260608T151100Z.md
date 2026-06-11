# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-08T15:11:00+00:00`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `5`
Prompt variants: `3`
Max output tokens: `512`
Reasoning effort: `medium`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bedrock | `openai.gpt-5.5` | 0 | 5 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

## Failures

- `bedrock` `openai.gpt-5.5` run 2: HTTP 401: <failed to read error response: Attempted to read or stream content, but the stream has been closed.>
- `bedrock` `openai.gpt-5.5` run 3: HTTP 401: <failed to read error response: Attempted to read or stream content, but the stream has been closed.>
- `bedrock` `openai.gpt-5.5` run 4: HTTP 401: <failed to read error response: Attempted to read or stream content, but the stream has been closed.>
- `bedrock` `openai.gpt-5.5` run 5: HTTP 401: <failed to read error response: Attempted to read or stream content, but the stream has been closed.>
- `bedrock` `openai.gpt-5.5` run 6: HTTP 401: <failed to read error response: Attempted to read or stream content, but the stream has been closed.>

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
