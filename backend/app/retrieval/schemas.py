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
