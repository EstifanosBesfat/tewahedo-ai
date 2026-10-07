"""Schemas for embedding, indexing, search, and retrieval evaluation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EmbeddingBatch(BaseModel):
    vectors: list[list[float]]
    token_lengths: list[int]
    window_counts: list[int]

    @model_validator(mode="after")
    def validate_lengths(self) -> "EmbeddingBatch":
        size = len(self.vectors)
        if len(self.token_lengths) != size or len(self.window_counts) != size:
            raise ValueError("embedding metadata must match vector count")
        return self


class TokenLimitItem(BaseModel):
    identifier: str
    token_length: int = Field(ge=0)
    window_count: int = Field(ge=1)


class IndexingReport(BaseModel):
    model_name: str
    collection_name: str
    source_path: str
    requested_chunks: int = Field(ge=0)
    indexed_chunks: int = Field(ge=0)
    collection_count: int = Field(ge=0)
    max_model_tokens: int = Field(ge=1)
    minimum_token_length: int = Field(ge=0)
    maximum_token_length: int = Field(ge=0)
    over_limit_chunks: list[TokenLimitItem] = Field(default_factory=list)


class SearchResult(BaseModel):
    similarity_score: float = Field(ge=-1, le=1)
    document_id: str
    chunk_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    text: str
    extraction_method: str
    source_quality_score: float = Field(ge=0, le=100)


class EvaluationQuestion(BaseModel):
    question_id: str
    category: Literal["direct", "paraphrased", "conceptual"]
    question: str = Field(min_length=1)
    review_focus: str = Field(min_length=1)


class EvaluationQuestionSet(BaseModel):
    document_id: str
    questions: list[EvaluationQuestion]

    @model_validator(mode="after")
    def validate_question_count(self) -> "EvaluationQuestionSet":
        if len(self.questions) != 15:
            raise ValueError("evaluation set must contain exactly 15 questions")
        category_counts = {
            category: sum(
                question.category == category for question in self.questions
            )
            for category in ("direct", "paraphrased", "conceptual")
        }
        if any(count != 5 for count in category_counts.values()):
            raise ValueError(
                "evaluation set must contain five questions per category"
            )
        return self


class EvaluationResult(BaseModel):
    question_id: str
    category: Literal["direct", "paraphrased", "conceptual"]
    question: str
    review_focus: str
    top_1: list[SearchResult]
    top_3: list[SearchResult]
    top_5: list[SearchResult]


class EvaluationRun(BaseModel):
    model_name: str
    collection_name: str
    question_count: int = Field(ge=0)
    results: list[EvaluationResult]


class AuditChunk(BaseModel):
    """One source span judged against a question."""

    chunk_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    status: Literal["verified", "manual_review", "documented_sense"]
    evidence: str = Field(min_length=1)


class QuestionJudgment(BaseModel):
    """Model-independent relevance judgment for one evaluation question."""

    question_id: str
    category: Literal["direct", "paraphrased", "conceptual"]
    expected_answer_concept: str = Field(min_length=1)
    ambiguity: Literal["low", "high"]
    metric_eligible: bool
    exclusion_reason: str | None = None
    chunks: list[AuditChunk]

    @model_validator(mode="after")
    def validate_metric_eligibility(self) -> "QuestionJudgment":
        verified = [chunk for chunk in self.chunks if chunk.status == "verified"]
        if self.metric_eligible and not verified:
            raise ValueError(
                f"{self.question_id} is metric-eligible but has no verified chunk"
            )
        if not self.metric_eligible and verified:
            raise ValueError(
                f"{self.question_id} is excluded from metrics but has verified chunks"
            )
        if self.ambiguity == "high" and self.metric_eligible:
            raise ValueError(
                f"{self.question_id} is high-ambiguity and cannot enter recall"
            )
        return self


class RankHit(BaseModel):
    top_1: bool
    top_3: bool
    top_5: bool
    matched_verified_chunk_ids: list[str]
    documented_sense_chunk_ids_in_top_5: list[str]


class RecallCount(BaseModel):
    hits: int = Field(ge=0)
    eligible: int = Field(ge=0)


class ModelRecallScore(BaseModel):
    """Question-level recall for one embedding model against frozen judgments."""

    model_name: str
    results_file: str
    question_count: int = Field(ge=0)
    metric_eligible_count: int = Field(ge=0)
    excluded_question_ids: list[str]
    recall_at_1: RecallCount
    recall_at_3: RecallCount
    recall_at_5: RecallCount
    questions: dict[str, RankHit]


class OverLimitWindow(BaseModel):
    chunk_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    cross_page: bool
    token_length: int = Field(ge=1)
    window_count: int = Field(ge=1)
    window_token_lengths: list[int]


class OverLimitWindowAudit(BaseModel):
    model_name: str
    max_model_tokens: int = Field(ge=1)
    over_limit_chunk_count: int = Field(ge=0)
    window_counts: list[int]
    second_window_token_minimum: int = Field(ge=0)
    second_window_token_maximum: int = Field(ge=0)
    cross_page_count: int = Field(ge=0)
    provenance_mismatches: int = Field(ge=0)
    chunks: list[OverLimitWindow]


class RetrievalAudit(BaseModel):
    """Frozen relevance judgments plus scored runs for later model comparison."""

    schema_version: Literal["1"]
    document_id: str
    labeling_policy: str = Field(min_length=1)
    recall_definition: str = Field(min_length=1)
    judgments: list[QuestionJudgment]
    model_scores: list[ModelRecallScore]
    over_limit_window_audit: OverLimitWindowAudit

    @model_validator(mode="after")
    def validate_judgment_set(self) -> "RetrievalAudit":
        if len(self.judgments) != 15:
            raise ValueError("retrieval audit must judge exactly 15 questions")
        return self
