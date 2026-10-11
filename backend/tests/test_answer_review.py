"""Tests for the human answer-review workflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.answers.passages import ParentCorpus
from app.answers.review import (
    PROTECTED_REVIEW_SOURCES,
    ReviewSubmission,
    ReviewValidationError,
    ReviewWorksheetQuestion,
    apply_answer_reviews,
    assert_review_output,
    build_review_worksheet,
    load_expected_concepts,
    load_ground_truth_questions,
    pending_submissions,
    render_review_packet,
    render_review_report,
    write_review_outputs,
)
from app.answers.review import ReviewInput
from app.answers.schemas import AnswerEvaluationDataset

BACKEND_ROOT = Path(__file__).resolve().parents[1]
EVALUATION = BACKEND_ROOT / "data" / "evaluation"
ANSWER_DATASET_PATH = EVALUATION / "answer-evaluation-bge-m3.json"
GROUND_TRUTH_PATH = EVALUATION / "ground-truth-v3.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
FROZEN_PATHS = [
    ANSWER_DATASET_PATH,
    EVALUATION / "answer-evaluation-bge-m3-report.md",
    GROUND_TRUTH_PATH,
    EVALUATION / "retrieval-evaluation-bge-m3.json",
    EVALUATION / "retrieval-evaluation-bge-m3-report.md",
    EVALUATION / "retrieval-evaluation-v3.json",
    CORPUS_PATH,
    BACKEND_ROOT / "data" / "processed" / "10commandments.retrieval-units.json",
]


def _question(
    question_id: str = "direct-01",
    eligible: bool = False,
    passages: list[tuple[int, str, str]] | None = None,
) -> ReviewWorksheetQuestion:
    rows = passages if passages is not None else [
        (1, "10commandments:chunk-0008", "አንደኛው ትእዛዝ «ከእኔ በቀር ሌሎች አማልክት አይሁኑልህ»"),
        (2, "10commandments:chunk-0040", "አባትህንና እናትህን አክብር"),
    ]
    return ReviewWorksheetQuestion(
        question_id=question_id,
        question="የመጀመሪያው ትእዛዝ ምንድን ነው?",
        category="direct",
        expected_concept=None,
        retrieval_metric_eligible=eligible,
        retrieval_exclusion_reason="three senses" if not eligible else None,
        automatic_abstention_code="contradictory_evidence",
        passages=[
            {
                "rank": rank,
                "parent_chunk_id": parent_id,
                "document_id": "10commandments",
                "source_filename": "10commandments.pdf",
                "page_start": 4 if rank == 1 else 14,
                "page_end": 4 if rank == 1 else 14,
                "text": text,
            }
            for rank, parent_id, text in rows
        ],
    )


def _apply(question: ReviewWorksheetQuestion, submission: ReviewSubmission):
    return apply_answer_reviews(
        [question],
        [submission],
        source_name="answer-evaluation-bge-m3.json",
        source_sha256="abc",
        ground_truth_file="ground-truth-v3.json",
        corpus_file="10commandments.chunks.json",
    )


def test_fabricated_chunk_document_and_page_are_rejected() -> None:
    question = _question()
    with pytest.raises(ValidationError):
        ReviewSubmission.model_validate(
            {
                "question_id": "direct-01",
                "status": "reviewed",
                "answerable": "yes",
                "selected_parent_chunk_ids": ["10commandments:chunk-0008"],
                "proposed_answer": "A grounded statement.",
                "proposed_answer_has_unsupported_part": False,
                "reviewer": "reviewer",
                "document_id": "invented-document",
                "page_start": 99,
            }
        )

    with pytest.raises(ReviewValidationError, match="chunk-9999"):
        _apply(
            question,
            ReviewSubmission(
                question_id="direct-01",
                status="reviewed",
                answerable="yes",
                selected_parent_chunk_ids=["10commandments:chunk-9999"],
                proposed_answer="This citation was not retrieved.",
                proposed_answer_has_unsupported_part=True,
                reviewer="reviewer",
            ),
        )


def test_missing_evidence_stays_separate_from_retrieval_eligibility() -> None:
    question = _question(eligible=False, passages=[])
    dataset = _apply(
        question,
        ReviewSubmission(
            question_id="direct-01",
            status="reviewed",
            answerable="no",
            proposed_answer="The available sources do not establish an answer.",
            proposed_answer_has_unsupported_part=False,
            reviewer="reviewer",
            reviewer_notes="No parent passage was available.",
        ),
    )
    record = dataset.records[0]

    assert record.evidence_label == "missing"
    assert record.selected_evidence == []
    assert record.answerable == "no"
    assert record.retrieval_metric_eligible is False
    assert record.proposed_answer != record.question


def test_contradictory_evidence_uses_only_retrieved_passages() -> None:
    question = _question(eligible=False)
    dataset = _apply(
        question,
        ReviewSubmission(
            question_id="direct-01",
            status="reviewed",
            answerable="ambiguous",
            selected_parent_chunk_ids=[
                "10commandments:chunk-0040",
                "10commandments:chunk-0008",
            ],
            qualifications_or_contradictions=(
                "The retrieved passages use the first commandment for different teachings."
            ),
            proposed_answer="The available sources do not establish one answer.",
            proposed_answer_has_unsupported_part=False,
            reviewer="reviewer",
        ),
    )
    record = dataset.records[0]

    assert record.evidence_label == "contradictory"
    assert record.retrieval_metric_eligible is False
    assert [item.parent_chunk_id for item in record.selected_evidence] == [
        "10commandments:chunk-0040",
        "10commandments:chunk-0008",
    ]
    assert {item.role for item in record.selected_evidence} == {"unresolved_evidence"}
    assert record.selected_evidence[0].document_id == "10commandments"
    assert record.selected_evidence[0].page_start == 14
    assert record.selected_evidence[0].text == "አባትህንና እናትህን አክብር"
    assert record.proposed_answer != record.selected_evidence[0].text
    assert record.retrieved_passages[0].text == question.passages[0].text


def test_answerable_yes_can_disagree_with_retrieval_exclusion() -> None:
    question = _question(eligible=False)
    dataset = _apply(
        question,
        ReviewSubmission(
            question_id="direct-01",
            status="reviewed",
            answerable="yes",
            selected_parent_chunk_ids=["10commandments:chunk-0008"],
            qualifications_or_contradictions="The page also names other objects of worship.",
            proposed_answer="The selected passage states the command about having no other gods.",
            proposed_answer_has_unsupported_part=False,
            reviewer="reviewer",
        ),
    )
    record = dataset.records[0]

    assert record.answerable == "yes"
    assert record.retrieval_metric_eligible is False
    assert record.evidence_label == "selected"
    assert record.selected_evidence[0].role == "supports_answer"
    assert record.selected_evidence[0].page_start == 4
    assert record.selected_evidence[0].page_end == 4


def test_review_status_rejects_partial_and_unfinished_reviews() -> None:
    with pytest.raises(ValidationError, match="pending"):
        ReviewSubmission(
            question_id="direct-02",
            status="pending",
            answerable="yes",
        )
    with pytest.raises(ValidationError, match="reviewer"):
        ReviewSubmission(
            question_id="direct-02",
            status="reviewed",
            answerable="no",
            proposed_answer="The sources do not establish an answer.",
            proposed_answer_has_unsupported_part=False,
        )
    question = _question(question_id="direct-02", eligible=True)
    with pytest.raises(ValidationError, match="at least one"):
        ReviewSubmission(
            question_id="direct-02",
            status="reviewed",
            answerable="yes",
            proposed_answer="A statement without a retrieved parent.",
            proposed_answer_has_unsupported_part=True,
            reviewer="reviewer",
        )
    dataset = _apply(
        question,
        ReviewSubmission(question_id="direct-02", status="pending"),
    )
    assert dataset.records[0].status == "pending"
    assert dataset.records[0].answerable is None
    assert dataset.records[0].evidence_label == "pending"


def test_proposed_answer_cannot_replace_the_source_text() -> None:
    question = _question()
    with pytest.raises(ReviewValidationError, match="separate"):
        _apply(
            question,
            ReviewSubmission(
                question_id="direct-01",
                status="reviewed",
                answerable="yes",
                selected_parent_chunk_ids=["10commandments:chunk-0008"],
                proposed_answer=question.passages[0].text,
                proposed_answer_has_unsupported_part=False,
                reviewer="reviewer",
            ),
        )


def test_real_worksheet_preserves_frozen_files_and_pending_reviews(tmp_path: Path) -> None:
    before = {path: path.read_bytes() for path in FROZEN_PATHS}
    dataset = AnswerEvaluationDataset.model_validate_json(
        ANSWER_DATASET_PATH.read_text(encoding="utf-8")
    )
    concepts = load_expected_concepts(GROUND_TRUTH_PATH)
    questions = load_ground_truth_questions(GROUND_TRUTH_PATH)
    corpus = ParentCorpus.load(CORPUS_PATH)
    worksheet = build_review_worksheet(dataset, concepts, questions, corpus)
    submissions = pending_submissions(worksheet)
    reviewed = apply_answer_reviews(
        worksheet,
        submissions,
        source_name=str(ANSWER_DATASET_PATH),
        source_sha256="unused-for-byte-check",
        ground_truth_file=str(GROUND_TRUTH_PATH),
        corpus_file=str(CORPUS_PATH),
    )
    packet = render_review_packet(worksheet)
    report = render_review_report(reviewed)
    write_review_outputs(
        packet,
        ReviewInput(schema_version="1", reviews=submissions),
        reviewed,
        tmp_path / "answer-review-packet-bge-m3.md",
        tmp_path / "answer-review-input-bge-m3.json",
        tmp_path / "answer-review-bge-m3.json",
        tmp_path / "answer-review-bge-m3-report.md",
        write_input=True,
    )

    assert {path: path.read_bytes() for path in FROZEN_PATHS} == before
    assert len(worksheet) == 15
    by_id = {record.question_id: record for record in reviewed.records}
    excluded = by_id["direct-01"]
    assert excluded.retrieval_metric_eligible is False
    assert excluded.answerable is None
    assert excluded.status == "pending"
    assert excluded.expected_concept is None
    assert excluded.retrieved_passages
    stored = corpus.record(excluded.retrieved_passages[0].parent_chunk_id)
    assert excluded.retrieved_passages[0].text == stored["text"]
    assert excluded.retrieved_passages[0].document_id == stored["document_id"]
    assert excluded.retrieved_passages[0].page_start == stored["page_start"]
    assert "Question: የመጀመሪያው ትእዛዝ ምንድን ነው?" in packet
    assert "Answerability is separate from retrieval-metric eligibility." in packet
    assert "Completed reviews: 0" in report
    assert "Pending cases: 15" in report
    assert "yes | 0 |" in report
    with pytest.raises(ValueError, match="frozen"):
        assert_review_output(ANSWER_DATASET_PATH)
    assert "answer-evaluation-bge-m3.json" in PROTECTED_REVIEW_SOURCES
    written = json.loads((tmp_path / "answer-review-bge-m3.json").read_text(encoding="utf-8"))
    assert written["question_count"] == 15
    assert written["records"][0]["retrieval_metric_eligible"] is False
