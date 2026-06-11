# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T16:30:53+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `4096`
Reasoning effort: `xhigh`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1135 | 184 | 497 ms | 3,293 ms | 4,330 ms | 116 | 167 | 103 | $8.2613 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1135`
Errored requests: `184`
Overall output throughput: `36.97` tokens/s
Completed requests per minute: `9.90`
Estimated OpenAI-equivalent cost total: `$8.2613`
Estimated OpenAI-equivalent cost mean/request: `$0.0073`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 496.89 | 897.31 | 1,408.65 | 899.41 | 329.73 | 149,901.29 | 5,281.18 |
| time_to_first_token_ms | 3,293.04 | 6,943.90 | 9,815.74 | 4,825.15 | 1,384.06 | 190,512.03 | 8,978.60 |
| end_to_end_latency_ms | 4,330.26 | 8,512.19 | 12,035.88 | 6,024.01 | 1,907.50 | 190,562.75 | 9,535.31 |
| request_output_throughput_token_per_s | 40.14 | 51.40 | 54.27 | 39.67 | 0.73 | 66.71 | 9.47 |
| number_input_tokens | 116.00 | 149.00 | 161.00 | 119.39 | 83.00 | 356.00 | 22.10 |
| number_output_tokens | 167.00 | 326.00 | 511.00 | 222.73 | 68.00 | 4,096.00 | 268.58 |
| number_reasoning_tokens | 103.00 | 254.00 | 419.00 | 158.84 | 29.00 | 4,096.00 | 266.37 |
| estimated_openai_cost_usd | 0.01 | 0.01 | 0.02 | 0.01 | 0.00 | 0.12 | 0.01 |


## Failures

- `openai` `gpt-5.5` run 488: HTTP 503: upstream connect error or disconnect/reset before headers. reset reason: connection timeout
- `openai` `gpt-5.5` run 589: HTTP 520: <!DOCTYPE html> <!--[if lt IE 7]> <html class="no-js ie6 oldie" lang="en-US"> <![endif]--> <!--[if IE 7]>    <html class="no-js ie7 oldie" lang="en-US"> <![endif]--> <!--[if IE 8]>    <html class="no-js ie8 oldie" lang="en-US"> <![endif]--> <!--[if gt IE 8]><!--> <html class="no-js" lang="en-US"> <!--<![endif]--> <head>  <title>api.openai.com | 520: Web server is returning an unknown error</title> <meta charset="UTF-8" /> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> <meta http-equiv="X-UA-Compatible" content="IE=Edge" /> <meta name="robots" content="noindex, nofollow" /> <meta name="viewport" content="width=device-width,initial-scale=1" /> <link rel="stylesheet" id="cf_styles-css" href="/cdn-cgi/styles/main.css" /> </head> <body> <div id="cf-wrapper">     <div id="cf-error-details" class="p-0">         <header class="mx-auto pt-10 lg:pt-6 lg:px-8 w-240 lg:w-full mb-8">             <h1 class="inline-block sm:block sm:mb-2 font-light text-60 lg:text-4xl text-black-dark leading-tight mr-2">                 <span class="inline-block">Web server is returning an unknown error</span>                 <span class="code-label">Error code 520</span>             </h1>             <div>                 Visit <a href="https://www.cloudflare.com/5xx-error-landing?utm_source=errorcode_520&utm_campaign=api.openai.com" target="_blank" rel="noopener noreferrer">cloudflare.com</a> for more information.             </div>             <div class="mt-3">2026-06-11 15:33:59...
- `openai` `gpt-5.5` run 1139: The read operation timed out
- `openai` `gpt-5.5` run 1140: [Errno -3] Temporary failure in name resolution
- `openai` `gpt-5.5` run 1141: [Errno -3] Temporary failure in name resolution
- `openai` `gpt-5.5` run 1142: [Errno -3] Temporary failure in name resolution
- `openai` `gpt-5.5` run 1143: [Errno -3] Temporary failure in name resolution
- `openai` `gpt-5.5` run 1144: [Errno -3] Temporary failure in name resolution
- `openai` `gpt-5.5` run 1145: [Errno -3] Temporary failure in name resolution
- `openai` `gpt-5.5` run 1146: [Errno -3] Temporary failure in name resolution
- ...and 174 more failures.

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
