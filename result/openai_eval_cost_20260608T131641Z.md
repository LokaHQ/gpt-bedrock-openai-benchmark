# OpenAI eval credit estimate

Generated at: `2026-06-08T13:16:41+00:00`
Dataset: `gsm8k/test`
Token counting: `tiktoken` via encoding_for_model for gpt-5.4, gpt-5.5.

| Model | Samples | Avg input tok | P95 input tok | Output tok/sample | Standard cost | Batch cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.4` | 1319 | 93.5 | 136 | 512 | $10.4381 | $5.2191 |
| `gpt-5.5` | 1319 | 93.5 | 136 | 512 | $20.8762 | $10.4381 |

Output tokens include the configured visible answer budget plus any configured hidden reasoning-token budget. OpenAI bills reasoning tokens as output tokens even though they are not visible in API responses.
