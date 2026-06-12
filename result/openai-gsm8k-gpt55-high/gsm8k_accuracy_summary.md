# GSM8K accuracy summary

Generated at: `2026-06-12T06:18:03+00:00`
Benchmark artifact: `result/openai-gsm8k-gpt55-high/openai_responses_latency_20260611T124720Z.jsonl`
Provider: `openai`
Model: `gpt-5.5`

| Metric | Value |
| --- | ---: |
| Total rows | 1319 |
| Successful rows | 1318 |
| Failed rows | 1 |
| Correct rows | 1284 |
| Incorrect rows | 34 |
| Missing model answer rows | 0 |
| Missing reference answer rows | 0 |
| Accuracy over all rows | 97.35% |
| Accuracy over successful rows | 97.42% |

Accuracy is computed by extracting the final `####` answer from the original GSM8K test set and from each saved model response, then comparing normalized final answers.

## Sample mismatches

| Prompt ID | Run | Reason | Expected | Model |
| --- | ---: | --- | --- | --- |
| gsm8k-test-12 | 14 | answer_mismatch | `13` | `12` |
| gsm8k-test-93 | 95 | answer_mismatch | `36` | `36.36` |
| gsm8k-test-119 | 121 | answer_mismatch | `95200` | `99076.92` |
| gsm8k-test-255 | 257 | answer_mismatch | `192` | `176` |
| gsm8k-test-306 | 308 | answer_mismatch | `10` | `5` |
| gsm8k-test-368 | 370 | answer_mismatch | `18` | `10` |
| gsm8k-test-403 | 405 | answer_mismatch | `81` | `135` |
| gsm8k-test-409 | 411 | answer_mismatch | `168000` | `42000` |
| gsm8k-test-423 | 425 | answer_mismatch | `8` | `-8` |
| gsm8k-test-454 | 456 | answer_mismatch | `150` | `240` |
