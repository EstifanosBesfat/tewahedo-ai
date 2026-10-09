"""Checks that the ground-truth validation stays tied to the question file."""

from __future__ import annotations

import json
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parents[1] / "data" / "evaluation"
ALLOWED_STATUS = {
    "VERIFIED",
    "PARTIALLY_SUPPORTED",
    "AMBIGUOUS",
    "NOT_SUPPORTED",
}


def test_validation_matches_the_fifteen_questions_without_changing_them() -> None:
    questions_path = EVALUATION_DIR / "amharic_retrieval_questions.json"
    validation_path = EVALUATION_DIR / "ground-truth-validation.json"
    before = questions_path.read_text(encoding="utf-8")
    questions = json.loads(before)
    validation = json.loads(validation_path.read_text(encoding="utf-8"))

    assert questions_path.read_text(encoding="utf-8") == before
    source_questions = questions["questions"]
    judged = validation["questions"]
    assert [item["question_id"] for item in judged] == [
        item["question_id"] for item in source_questions
    ]
    assert [item["question"] for item in judged] == [
        item["question"] for item in source_questions
    ]
    assert [item["question_type"] for item in judged] == [
        item["category"] for item in source_questions
    ]
    assert all(item["status"] in ALLOWED_STATUS for item in judged)
    assert all(item["source_evidence"] for item in judged)
    assert all(
        evidence["amharic_text"].strip() and evidence["page"] >= 1
        for item in judged
        for evidence in item["source_evidence"]
    )
    by_id = {item["question_id"]: item for item in judged}
    assert by_id["direct-01"]["status"] == "AMBIGUOUS"
    assert by_id["direct-01"]["recommended_ground_truth"]
    counts = {
        status: sum(item["status"] == status for item in judged)
        for status in ALLOWED_STATUS
    }
    assert counts == {
        "VERIFIED": 8,
        "PARTIALLY_SUPPORTED": 6,
        "AMBIGUOUS": 1,
        "NOT_SUPPORTED": 0,
    }
