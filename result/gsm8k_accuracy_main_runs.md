# GSM8K accuracy comparison

Generated at: `2026-06-12T06:18:03+00:00`

| Label | Provider | Model | Correct | Incorrect | Accuracy (all) | Accuracy (successful) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| bedrock-medium | bedrock | `openai.gpt-5.5` | 1287 | 32 | 97.57% | 97.57% |
| openai-medium | openai | `gpt-5.5` | 1285 | 32 | 97.42% | 97.57% |
| bedrock-high | bedrock | `openai.gpt-5.5` | 1287 | 32 | 97.57% | 97.57% |
| openai-high | openai | `gpt-5.5` | 1284 | 34 | 97.35% | 97.42% |
| bedrock-xhigh | bedrock | `openai.gpt-5.5` | 1285 | 34 | 97.42% | 97.42% |
| openai-xhigh-merged-clean | openai | `gpt-5.5` | 1284 | 35 | 97.35% | 97.35% |

## Bedrock vs OpenAI deltas

- `medium`: OpenAI 97.42% vs Bedrock 97.57% (-0.15 percentage points).
- `high`: OpenAI 97.35% vs Bedrock 97.57% (-0.22 percentage points).
- `xhigh`: OpenAI 97.35% vs Bedrock 97.42% (-0.07 percentage points).
