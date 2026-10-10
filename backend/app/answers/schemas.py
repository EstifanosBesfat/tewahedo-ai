"""Schemas for source-grounded answers and their review records."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RetrievedUnitRef(BaseModel):
    """One ranked retrieval unit that collapsed into a parent chunk."""

    rank: int = Field(ge=1)
    unit_id: str = Field(min_length=1)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    similarity_score: float = Field(ge=-1, le=1)


class SourcePassage(BaseModel):
    """Parent-chunk text copied from the stored corpus."""

    rank: int = Field(ge=1)
    document_id: str = Field(min_length=1)
    source_filename: str = Field(min_length=1)
    parent_chunk_id: str = Field(min_length=1)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    extraction_method: str = Field(min_length=1)
    source_quality_score: float = Field(ge=0, le=100)
    text: str = Field(min_length=1)
    retrieved_units: list[RetrievedUnitRef]

    @model_validator(mode="after")
    def validate_page_range(self) -> "SourcePassage":
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        return self


class Citation(BaseModel):
    """A reference copied from a retrieved parent passage."""

    document_id: str = Field(min_length=1)
    source_filename: str = Field(min_length=1)
    parent_chunk_id: str = Field(min_length=1)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    excerpt: str = Field(min_length=1)
    role: Literal["supports_answer", "unresolved_evidence"]


class AnswerGenerationRequest(BaseModel):
    """Question plus the passages a provider is allowed to use."""

    question_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    language: Literal["am", "en"] = "am"
    passages: list[SourcePassage]
    contradictory: bool = False
    selected_parent_chunk_ids: list[str] | None = None


class AnswerDraft(BaseModel):
    """Provider output before citations are attached from passage metadata.

    A draft can name parent chunk ids. It cannot supply document titles,
    page numbers, or a judgment that the answer is correct.
    """

    answer_text: str = Field(min_length=1)
    abstained: bool
    abstention_code: Literal[
        "missing_evidence",
        "contradictory_evidence",
        "multiple_passages",
        "rejected_citations",
        "none",
    ]
    cited_parent_chunk_ids: list[str]
    citation_role: Literal["supports_answer", "unresolved_evidence"]
    excerpts_by_parent_chunk_id: dict[str, str] | None = None


class GeneratedAnswer(BaseModel):
    """Answer text kept separate from the source passages."""

    question_id: str
    language: Literal["am", "en"]
    answer_text: str = Field(min_length=1)
    abstained: bool
    abstention_code: Literal[
        "missing_evidence",
        "contradictory_evidence",
        "multiple_passages",
        "rejected_citations",
        "none",
    ]
    abstention_reason: str | None = None
    citations: list[Citation]
    supporting_parent_chunk_ids: list[str]
    rejected_citation_ids: list[str]
    discarded_answer_text: str | None = None
    provider_name: str = Field(min_length=1)
    model_name: str | None = None


class EvidenceAssessment(BaseModel):
    """Rule-based evidence gate. This is not a factual-support judgment."""

    status: Literal[
        "missing",
        "contradictory",
        "multiple_passages",
        "rejected_selection",
        "single_passage",
    ]
    reason: str = Field(min_length=1)
    origin: Literal["passage_count", "caller_flag", "selection"]
    selected_parent_chunk_id: str | None = None


class HumanAnswerReview(BaseModel):
    """Judgments recorded only after a person reviews the answer."""

    status: Literal["pending", "reviewed"] = "pending"
    answerability: Literal[
        "answerable",
        "partially_answerable",
        "not_answerable",
        "contradictory",
    ] | None = None
    factual_support: Literal[
        "supported",
        "partially_supported",
        "unsupported",
        "not_applicable",
    ] | None = None
    important_qualifications_omitted: bool | None = None
    contains_unsupported_claims: bool | None = None
    reviewer_notes: str = ""
    reviewer: str | None = None

    @model_validator(mode="after")
    def validate_review_state(self) -> "HumanAnswerReview":
        judgments = (
            self.answerability,
            self.factual_support,
            self.important_qualifications_omitted,
            self.contains_unsupported_claims,
            self.reviewer,
        )
        if self.status == "pending" and any(item is not None for item in judgments):
            raise ValueError("a pending review cannot contain human judgments")
        if self.status == "reviewed" and (
            self.answerability is None
            or self.factual_support is None
            or self.important_qualifications_omitted is None
            or self.contains_unsupported_claims is None
            or self.reviewer is None
        ):
            raise ValueError("a completed review needs every human judgment")
        return self


class AutomaticChecks(BaseModel):
    """Mechanical citation and provenance checks."""

    label: Literal["automatic"] = "automatic"
    citation_count: int = Field(ge=0)
    citations_match_retrieved_passages: bool
    unmatched_citations: list[str]
    excerpts_are_exact_substrings: bool
    page_ranges_match_parent_records: bool
    document_ids_match_parent_records: bool
    answer_text_differs_from_each_source_passage: bool
    source_passages_match_corpus: bool
    abstained: bool
    evidence_status: str


class RankedParent(BaseModel):
    rank: int = Field(ge=1)
    parent_chunk_id: str
    document_id: str
    source_filename: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)


class AnswerEvaluationRecord(BaseModel):
    """One question, its retrieved evidence, and the separated answer."""

    question_id: str
    question: str
    category: Literal["direct", "paraphrased", "conceptual"]
    retrieval_metric_eligible: bool
    retrieval_exclusion_reason: str | None = None
    retrieved_parent_ranking: list[RankedParent]
    source_passages_retrieved: list[SourcePassage]
    source_passages_used: list[SourcePassage]
    generated_answer: GeneratedAnswer
    evidence: EvidenceAssessment
    automatic_checks: AutomaticChecks
    human_review: HumanAnswerReview


class AnswerEvaluationDataset(BaseModel):
    schema_version: Literal["1"]
    description: str = Field(min_length=1)
    retrieval_model: Literal["BAAI/bge-m3"]
    answer_provider: str
    answer_model: str | None
    question_file: str
    retrieval_results_file: str
    corpus_file: str
    question_count: int = Field(ge=0)
    frozen_input_sha256: dict[str, str]
    records: list[AnswerEvaluationRecord]

    @model_validator(mode="after")
    def validate_count(self) -> "AnswerEvaluationDataset":
        if self.question_count != len(self.records):
            raise ValueError("question_count must match the number of records")
        return self
