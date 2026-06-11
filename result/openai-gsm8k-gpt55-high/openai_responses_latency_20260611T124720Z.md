# OpenAI-compatible Responses API latency benchmark

Generated at: `2026-06-11T12:47:20+00:00`
Dataset: `gsm8k/test`
Bedrock region: `us-east-2`
Warmups per model: `1`
Measured runs per model: `1319`
Max output tokens: `2048`
Reasoning effort: `high`

## Summary

| Provider | Model | OK | Failed | TTFB p50 | TTFT p50 | Total p50 | Input tok p50 | Output tok p50 | Reasoning tok p50 | Est OpenAI cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-5.5` | 1318 | 1 | 497 ms | 2,356 ms | 3,248 ms | 116 | 132 | 69 | $6.8990 |

## LLMPerf-style aggregate metrics

### openai `gpt-5.5`

Completed requests: `1318`
Errored requests: `1`
Overall output throughput: `38.72` tokens/s
Completed requests per minute: `15.03`
Estimated OpenAI-equivalent cost total: `$6.8990`
Estimated OpenAI-equivalent cost mean/request: `$0.0052`

| Metric | p50 | p90 | p95 | Mean | Min | Max | Stddev |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| time_to_first_byte_ms | 497.31 | 822.49 | 1,114.03 | 779.43 | 319.00 | 124,567.52 | 4,300.01 |
| time_to_first_token_ms | 2,355.96 | 4,280.41 | 5,742.08 | 2,999.56 | 1,077.01 | 126,615.05 | 4,706.80 |
| end_to_end_latency_ms | 3,248.10 | 5,712.33 | 6,971.20 | 3,991.66 | 1,504.40 | 127,949.81 | 5,553.43 |
| request_output_throughput_token_per_s | 42.32 | 52.35 | 55.48 | 41.33 | 0.94 | 66.74 | 9.27 |
| number_input_tokens | 116.00 | 149.00 | 162.00 | 119.47 | 83.00 | 245.00 | 21.55 |
| number_output_tokens | 132.00 | 227.00 | 310.00 | 154.57 | 39.00 | 1,136.00 | 97.50 |
| number_reasoning_tokens | 69.00 | 145.00 | 222.00 | 90.40 | 14.00 | 1,034.00 | 90.55 |
| estimated_openai_cost_usd | 0.00 | 0.01 | 0.01 | 0.01 | 0.00 | 0.03 | 0.00 |


## Failures

- `openai` `gpt-5.5` run 722: HTTP 520: <!DOCTYPE html> <!--[if lt IE 7]> <html class="no-js ie6 oldie" lang="en-US"> <![endif]--> <!--[if IE 7]>    <html class="no-js ie7 oldie" lang="en-US"> <![endif]--> <!--[if IE 8]>    <html class="no-js ie8 oldie" lang="en-US"> <![endif]--> <!--[if gt IE 8]><!--> <html class="no-js" lang="en-US"> <!--<![endif]--> <head>  <title>api.openai.com | 520: Web server is returning an unknown error</title> <meta charset="UTF-8" /> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> <meta http-equiv="X-UA-Compatible" content="IE=Edge" /> <meta name="robots" content="noindex, nofollow" /> <meta name="viewport" content="width=device-width,initial-scale=1" /> <link rel="stylesheet" id="cf_styles-css" href="/cdn-cgi/styles/main.css" /> </head> <body> <div id="cf-wrapper">     <div id="cf-error-details" class="p-0">         <header class="mx-auto pt-10 lg:pt-6 lg:px-8 w-240 lg:w-full mb-8">             <h1 class="inline-block sm:block sm:mb-2 font-light text-60 lg:text-4xl text-black-dark leading-tight mr-2">                 <span class="inline-block">Web server is returning an unknown error</span>                 <span class="code-label">Error code 520</span>             </h1>             <div>                 Visit <a href="https://www.cloudflare.com/5xx-error-landing?utm_source=errorcode_520&utm_campaign=api.openai.com" target="_blank" rel="noopener noreferrer">cloudflare.com</a> for more information.             </div>             <div class="mt-3">2026-06-11 12:06:13...

## Method

TTFB is measured from request start to the first non-empty streamed line. TTFT is measured from request start to the first streamed output-text delta. Total latency is measured through stream completion. Runs are sequential by default to avoid measuring client-side concurrency effects.
