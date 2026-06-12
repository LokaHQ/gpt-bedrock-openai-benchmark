from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "score_gsm8k_accuracy.py"
SPEC = importlib.util.spec_from_file_location("score_gsm8k_accuracy", SCRIPT_PATH)
assert SPEC is not None
scorer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = scorer
SPEC.loader.exec_module(scorer)


def test_extract_final_answer_uses_last_marker() -> None:
    text = "scratch\n#### 12\nnotes\n#### 18"

    assert scorer.extract_final_answer(text) == "18"


def test_normalize_answer_handles_currency_commas_and_decimals() -> None:
    assert scorer.normalize_answer("$1,200.00") == "1200"
    assert scorer.normalize_answer("18.") == "18"
    assert scorer.normalize_answer("−42") == "-42"


def test_score_record_marks_missing_model_answer_in_ok_row() -> None:
    row = {
        "prompt_id": "gsm8k-test-0",
        "run_index": 2,
        "provider": "openai",
        "model": "gpt-5.5",
        "ok": True,
        "prompt_index": 0,
        "output_text": None,
    }
    references = {
        "gsm8k-test-0": scorer.Gsm8kReference(
            prompt_id="gsm8k-test-0",
            answer_text="work\n#### 18",
        )
    }

    record = scorer.score_record(row, references)

    assert record.is_correct is False
    assert record.mismatch_reason == "missing_model_answer"


def test_score_record_accepts_numeric_equivalent_answers() -> None:
    row = {
        "prompt_id": "gsm8k-test-1",
        "run_index": 3,
        "provider": "bedrock",
        "model": "openai.gpt-5.5",
        "ok": True,
        "prompt_index": 1,
        "output_text": "#### $3.00",
    }
    references = {
        "gsm8k-test-1": scorer.Gsm8kReference(
            prompt_id="gsm8k-test-1",
            answer_text="calc\n#### 3",
        )
    }

    record = scorer.score_record(row, references)

    assert record.is_correct is True
    assert record.normalized_model_answer == "3"
