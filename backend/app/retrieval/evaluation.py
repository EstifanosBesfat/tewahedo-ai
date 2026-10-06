"""Deterministic retrieval evaluation runner without answer generation."""

from __future__ import annotations

import json
from pathlib import Path

from app.retrieval.schemas import (
    EvaluationQuestionSet,
    EvaluationResult,
    EvaluationRun,
)
from app.retrieval.service import RetrievalService


def run_evaluation(
    service: RetrievalService,
    questions_path: Path,
) -> EvaluationRun:
    question_set = EvaluationQuestionSet.model_validate_json(
        questions_path.read_text(encoding="utf-8")
    )
    results: list[EvaluationResult] = []
    for item in question_set.questions:
        top_five = service.search(item.question, top_k=5)
        results.append(
            EvaluationResult(
                question_id=item.question_id,
                category=item.category,
                question=item.question,
                review_focus=item.review_focus,
                top_1=top_five[:1],
                top_3=top_five[:3],
                top_5=top_five,
            )
        )
    return EvaluationRun(
        model_name=service.embedding_provider.model_name,
        collection_name=service.vector_store.collection_name,
        question_count=len(results),
        results=results,
    )


def write_evaluation(run: EvaluationRun, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(run.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
