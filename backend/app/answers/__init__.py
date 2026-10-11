"""Source-grounded answer generation and evaluation.

This package does not retrieve, embed, or rank passages. It consumes
results from the existing retrieval service and checks that any answer
stays tied to those passages.
"""

from app.answers.citations import automatic_checks, resolve_citations
from app.answers.dataset import build_answer_dataset, render_answer_report
from app.answers.passages import ParentCorpus, passages_from_search_results
from app.answers.review import (
    ReviewSubmission,
    apply_answer_reviews,
    build_review_worksheet,
)
from app.answers.providers import (
    AnswerProvider,
    ConfiguredAnswerProvider,
    ExtractiveAnswerProvider,
)
from app.answers.schemas import (
    AnswerEvaluationDataset,
    AnswerGenerationRequest,
    GeneratedAnswer,
    SourcePassage,
)

__all__ = [
    "AnswerEvaluationDataset",
    "AnswerGenerationRequest",
    "AnswerProvider",
    "ConfiguredAnswerProvider",
    "ExtractiveAnswerProvider",
    "GeneratedAnswer",
    "ParentCorpus",
    "ReviewSubmission",
    "SourcePassage",
    "apply_answer_reviews",
    "automatic_checks",
    "build_answer_dataset",
    "build_review_worksheet",
    "passages_from_search_results",
    "render_answer_report",
    "resolve_citations",
]
