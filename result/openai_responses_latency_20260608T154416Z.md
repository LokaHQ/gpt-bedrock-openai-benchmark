# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-08T15:44:16+00:00`
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

- `bedrock` `openai.gpt-5.5` run 2: HTTP 401: {"error":{"code":"access_denied","message":"Your subscription to the model could not be established. Reason: AccessDeniedError [AccessDeniedException]: User: arn:aws:sts::396587179375:assumed-role/AWSReservedSSO_MLEngineers_0eece12190618f35/petar.kalinovski@loka.com is not authorized to perform: aw...
- `bedrock` `openai.gpt-5.5` run 3: HTTP 401: {"error":{"code":"access_denied","message":"Your subscription to the model could not be established. Reason: AccessDeniedError [AccessDeniedException]: User: arn:aws:sts::396587179375:assumed-role/AWSReservedSSO_MLEngineers_0eece12190618f35/petar.kalinovski@loka.com is not authorized to perform: aw...
- `bedrock` `openai.gpt-5.5` run 4: HTTP 401: {"error":{"code":"access_denied","message":"Your subscription to the model could not be established. Reason: AccessDeniedError [AccessDeniedException]: User: arn:aws:sts::396587179375:assumed-role/AWSReservedSSO_MLEngineers_0eece12190618f35/petar.kalinovski@loka.com is not authorized to perform: aw...
- `bedrock` `openai.gpt-5.5` run 5: HTTP 401: {"error":{"code":"access_denied","message":"Your subscription to the model could not be established. Reason: AccessDeniedError [AccessDeniedException]: User: arn:aws:sts::396587179375:assumed-role/AWSReservedSSO_MLEngineers_0eece12190618f35/petar.kalinovski@loka.com is not authorized to perform: aw...
- `bedrock` `openai.gpt-5.5` run 6: HTTP 401: {"error":{"code":"access_denied","message":"Your subscription to the model could not be established. Reason: AccessDeniedError [AccessDeniedException]: User: arn:aws:sts::396587179375:assumed-role/AWSReservedSSO_MLEngineers_0eece12190618f35/petar.kalinovski@loka.com is not authorized to perform: aw...

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
