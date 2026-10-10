"""Tests for source-grounded answer evaluation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.answers.citations import automatic_checks, resolve_citations
from app.answers.dataset import (
    FROZEN_EVALUATION_FILES,
    assert_writable_output,
    build_answer_dataset,
    render_answer_report,
    write_answer_outputs,
)
from app.answers.passages import ParentCorpus, passages_from_search_results
from app.answers.providers import (
    ABSTAIN_CONTRADICTORY,
    ABSTAIN_MISSING,
    ABSTAIN_MULTIPLE,
    ConfiguredAnswerProvider,
    ExtractiveAnswerProvider,
    assess_evidence,
)
from app.answers.schemas import (
    AnswerDraft,
    AnswerGenerationRequest,
    Citation,
    EvidenceAssessment,
    HumanAnswerReview,
)
from app.retrieval.schemas import SearchResult

BACKEND_ROOT = Path(__file__).resolve().parents[1]
EVALUATION = BACKEND_ROOT / "data" / "evaluation"
QUESTIONS_PATH = EVALUATION / "amharic_retrieval_questions.json"
RETRIEVAL_PATH = EVALUATION / "retrieval-evaluation-bge-m3.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
FROZEN_PATHS = [
    QUESTIONS_PATH,
    RETRIEVAL_PATH,
    CORPUS_PATH,
    EVALUATION / "ground-truth-v3.json",
    EVALUATION / "retrieval-evaluation-v3.json",
    EVALUATION / "retrieval-evaluation-bge-m3-report.md",
    EVALUATION / "retrieval-evaluation-bge-m3-resources.json",
    BACKEND_ROOT / "data" / "processed" / "10commandments.retrieval-units.json",
]


def _corpus() -> ParentCorpus:
    return ParentCorpus(
        {
            "document_id": "10commandments",
            "source_filename": "10commandments.pdf",
            "chunks": [
                {
                    "chunk_id": "10commandments:chunk-0008",
                    "document_id": "10commandments",
                    "page_start": 4,
                    "page_end": 4,
                    "text": "አንደኛው ትእዛዝ «ከእኔ በቀር ሌሎች አማልክት አይሁኑልህ»",
                    "extraction_method": "ocr",
                    "source_quality_score": 82.53,
                },
                {
                    "chunk_id": "10commandments:chunk-0040",
                    "document_id": "10commandments",
                    "page_start": 14,
                    "page_end": 15,
                    "text": "አባትህንና እናትህን አክብር",
                    "extraction_method": "ocr",
                    "source_quality_score": 80.0,
                },
            ],
        }
    )


def _hit(
    chunk_id: str,
    text: str,
    page_start: int = 1,
    page_end: int = 1,
    score: float = 0.5,
) -> SearchResult:
    return SearchResult(
        similarity_score=score,
        document_id="10commandments",
        chunk_id=chunk_id,
        page_start=page_start,
        page_end=page_end,
        text=text,
        extraction_method="ocr",
        source_quality_score=1,
    )


def _request(
    passages,
    contradictory: bool = False,
    selected: list[str] | None = None,
    language: str = "am",
) -> AnswerGenerationRequest:
    return AnswerGenerationRequest(
        question_id="direct-01",
        question="የመጀመሪያው ትእዛዝ ምንድን ነው?",
        language=language,
        passages=passages,
        contradictory=contradictory,
        selected_parent_chunk_ids=selected,
    )


def test_search_results_keep_parent_metadata_and_exact_corpus_text() -> None:
    corpus = _corpus()
    hits = [
        _hit(
            "10commandments:chunk-0008:unit-02",
            "unit text that must stay out of the parent passage",
            page_start=9,
            page_end=9,
            score=0.8,
        ),
        _hit(
            "10commandments:chunk-0008:unit-01",
            "another unit",
            page_start=9,
            page_end=9,
            score=0.7,
        ),
        _hit(
            "10commandments:chunk-0040:unit-01",
            "different unit text",
            page_start=2,
            page_end=2,
            score=0.4,
        ),
    ]

    passages = passages_from_search_results(hits, corpus, width=5)

    assert [passage.parent_chunk_id for passage in passages] == [
        "10commandments:chunk-0008",
        "10commandments:chunk-0040",
    ]
    first = passages[0]
    assert first.document_id == "10commandments"
    assert first.source_filename == "10commandments.pdf"
    assert first.page_start == 4
    assert first.page_end == 4
    assert first.text == "አንደኛው ትእዛዝ «ከእኔ በቀር ሌሎች አማልክት አይሁኑልህ»"
    assert first.text == corpus.text(first.parent_chunk_id)
    assert [unit.unit_id for unit in first.retrieved_units] == [
        "10commandments:chunk-0008:unit-02",
        "10commandments:chunk-0008:unit-01",
    ]
    assert first.retrieved_units[0].page_start == 9
    assert "unit text" not in first.text


def test_citations_match_retrieved_chunks_and_reject_inventions() -> None:
    passages = passages_from_search_results(
        [_hit("10commandments:chunk-0008:unit-01", "unit", page_start=4, page_end=4)],
        _corpus(),
    )

    citations, rejected = resolve_citations(
        ["10commandments:chunk-0008"],
        passages,
        "supports_answer",
        {"10commandments:chunk-0008": "ከእኔ በቀር"},
    )
    invented, invented_rejected = resolve_citations(
        ["10commandments:chunk-9999"],
        passages,
        "supports_answer",
    )
    altered, altered_rejected = resolve_citations(
        ["10commandments:chunk-0008"],
        passages,
        "supports_answer",
        {"10commandments:chunk-0008": "ገጽ 99 ላይ የተጻፈ አዲስ ጥቅስ"},
    )

    assert rejected == []
    assert citations[0].document_id == "10commandments"
    assert citations[0].source_filename == "10commandments.pdf"
    assert citations[0].parent_chunk_id == "10commandments:chunk-0008"
    assert citations[0].page_start == 4
    assert citations[0].page_end == 4
    assert citations[0].excerpt == "ከእኔ በቀር"
    assert invented == []
    assert invented_rejected == ["10commandments:chunk-9999"]
    assert altered == []
    assert altered_rejected == ["10commandments:chunk-0008"]


def test_wrong_page_on_a_citation_fails_the_automatic_check() -> None:
    passages = passages_from_search_results(
        [_hit("10commandments:chunk-0008:unit-01", "unit", page_start=4, page_end=4)],
        _corpus(),
    )
    provider = ExtractiveAnswerProvider()
    answer = provider.generate(_request(passages))
    answer.citations[0] = Citation(
        document_id="other-document",
        source_filename="invented.pdf",
        parent_chunk_id=passages[0].parent_chunk_id,
        page_start=99,
        page_end=100,
        excerpt="not in the passage",
        role="supports_answer",
    )
    evidence = EvidenceAssessment(
        status="single_passage",
        reason="One retrieved source passage is available to quote.",
        origin="passage_count",
        selected_parent_chunk_id=passages[0].parent_chunk_id,
    )

    checks = automatic_checks(answer, passages, evidence)

    assert checks.citations_match_retrieved_passages is False
    assert checks.page_ranges_match_parent_records is False
    assert checks.document_ids_match_parent_records is False
    assert checks.excerpts_are_exact_substrings is False
    assert checks.unmatched_citations == ["10commandments:chunk-0008"]


def test_missing_and_contradictory_evidence_abstain_without_a_teaching() -> None:
    provider = ExtractiveAnswerProvider()
    passages = passages_from_search_results(
        [
            _hit("10commandments:chunk-0008:unit-01", "unit-a", score=0.9),
            _hit("10commandments:chunk-0040:unit-01", "unit-b", score=0.2),
        ],
        _corpus(),
    )

    missing = provider.generate(_request([]))
    contradictory = provider.generate(_request(passages, contradictory=True))
    multiple = provider.generate(_request(passages))

    assert assess_evidence([]).status == "missing"
    assert missing.abstained is True
    assert missing.abstention_code == "missing_evidence"
    assert missing.answer_text == ABSTAIN_MISSING["am"]
    assert missing.citations == []
    assert missing.supporting_parent_chunk_ids == []
    assert contradictory.abstained is True
    assert contradictory.abstention_code == "contradictory_evidence"
    assert contradictory.answer_text == ABSTAIN_CONTRADICTORY["am"]
    assert contradictory.supporting_parent_chunk_ids == []
    assert {citation.role for citation in contradictory.citations} == {
        "unresolved_evidence"
    }
    assert [citation.parent_chunk_id for citation in contradictory.citations] == [
        "10commandments:chunk-0008",
        "10commandments:chunk-0040",
    ]
    assert multiple.abstention_code == "multiple_passages"
    assert multiple.answer_text == ABSTAIN_MULTIPLE["am"]
    assert all(
        passage.text not in contradictory.answer_text for passage in passages
    )


def test_single_passage_quotes_the_source_without_replacing_it() -> None:
    corpus = _corpus()
    passages = passages_from_search_results(
        [_hit("10commandments:chunk-0040:unit-01", "unit text is not the answer")],
        corpus,
    )
    answer = ExtractiveAnswerProvider().generate(
        _request(passages, language="en")
    )

    assert answer.abstained is False
    assert answer.answer_text != passages[0].text
    assert passages[0].text in answer.answer_text
    assert answer.citations[0].excerpt == passages[0].text
    assert answer.citations[0].page_start == 14
    assert answer.citations[0].page_end == 15
    assert answer.model_name is None
    assert passages[0].text == "አባትህንና እናትህን አክብር"


def test_configured_provider_drops_invented_citations_and_self_approval() -> None:
    passages = passages_from_search_results(
        [_hit("10commandments:chunk-0008:unit-01", "unit")],
        _corpus(),
    )

    def complete(request: AnswerGenerationRequest) -> AnswerDraft:
        return AnswerDraft(
            answer_text="This answer is certainly an established teaching.",
            abstained=False,
            abstention_code="none",
            cited_parent_chunk_ids=["10commandments:chunk-9999"],
            citation_role="supports_answer",
        )

    with pytest.raises(ValueError, match="model_name"):
        ConfiguredAnswerProvider(model_name="  ", complete=complete)

    answer = ConfiguredAnswerProvider(
        model_name="example-model",
        complete=complete,
    ).generate(_request(passages, language="en"))
    review = HumanAnswerReview()

    assert answer.model_name == "example-model"
    assert answer.abstained is True
    assert answer.abstention_code == "rejected_citations"
    assert answer.citations == []
    assert answer.rejected_citation_ids == ["10commandments:chunk-9999"]
    assert answer.discarded_answer_text == (
        "This answer is certainly an established teaching."
    )
    assert answer.answer_text != answer.discarded_answer_text
    assert review.status == "pending"
    assert review.factual_support is None


def test_selected_unknown_parent_abstains() -> None:
    passages = passages_from_search_results(
        [_hit("10commandments:chunk-0008:unit-01", "unit")],
        _corpus(),
    )
    answer = ExtractiveAnswerProvider().generate(
        _request(passages, selected=["10commandments:chunk-0040"])
    )

    assert answer.abstained is True
    assert answer.abstention_code == "rejected_citations"
    assert answer.supporting_parent_chunk_ids == []


def test_dataset_preserves_frozen_artifacts_and_separates_judgments(
    tmp_path: Path,
) -> None:
    before = {path: path.read_bytes() for path in FROZEN_PATHS}

    dataset = build_answer_dataset(QUESTIONS_PATH, RETRIEVAL_PATH, CORPUS_PATH)
    json_path = tmp_path / "answer-evaluation-bge-m3.json"
    report_path = tmp_path / "answer-evaluation-bge-m3-report.md"
    write_answer_outputs(dataset, json_path, report_path)
    report = report_path.read_text(encoding="utf-8")

    assert {path: path.read_bytes() for path in FROZEN_PATHS} == before
    assert dataset.question_count == 15
    assert dataset.retrieval_model == "BAAI/bge-m3"
    assert dataset.answer_model is None
    by_id = {record.question_id: record for record in dataset.records}
    excluded = by_id["direct-01"]
    assert excluded.retrieval_metric_eligible is False
    assert excluded.generated_answer.abstained is True
    assert excluded.generated_answer.abstention_code == "contradictory_evidence"
    assert excluded.source_passages_used == []
    assert excluded.human_review.status == "pending"
    assert excluded.human_review.factual_support is None
    assert excluded.automatic_checks.label == "automatic"
    for record in dataset.records:
        assert record.automatic_checks.citations_match_retrieved_passages is True
        assert record.automatic_checks.source_passages_match_corpus is True
        assert record.automatic_checks.answer_text_differs_from_each_source_passage
        assert record.human_review.status == "pending"
        for passage in record.source_passages_retrieved:
            assert passage.text
            assert record.generated_answer.answer_text != passage.text
    assert "Automatic checks" in report
    assert "Human judgments" in report
    assert "Answers marked supported by sources | 0 |" in report
    assert "Records awaiting human review | 15 |" in report
    with pytest.raises(ValueError, match="frozen"):
        assert_writable_output(EVALUATION / "ground-truth-v3.json")
    assert "ground-truth-v3.json" in FROZEN_EVALUATION_FILES


def test_written_dataset_keeps_the_question_and_parent_ranking() -> None:
    dataset = build_answer_dataset(QUESTIONS_PATH, RETRIEVAL_PATH, CORPUS_PATH)
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    retrieval = json.loads(RETRIEVAL_PATH.read_text(encoding="utf-8"))
    retrieval_by_id = {row["question_id"]: row for row in retrieval["questions"]}

    assert [item["question_id"] for item in questions["questions"]] == [
        record.question_id for record in dataset.records
    ]
    for record, item in zip(dataset.records, questions["questions"], strict=True):
        assert record.question == item["question"]
        assert record.category == item["category"]
        ranked = retrieval_by_id[record.question_id]
        assert [parent.parent_chunk_id for parent in record.retrieved_parent_ranking] == [
            row["parent_chunk_id"] for row in ranked["parent_ranking"]
        ]
        assert record.source_passages_retrieved[0].document_id == "10commandments"
        assert record.source_passages_retrieved[0].source_filename == "10commandments.pdf"
