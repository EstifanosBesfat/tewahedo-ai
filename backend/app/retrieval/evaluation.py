"""Deterministic retrieval evaluation runner without answer generation."""

from __future__ import annotations

import json
from pathlib import Path

from app.retrieval.schemas import (
    EvaluationQuestionSet,
    EvaluationResult,
    EvaluationRun,
    ModelRecallScore,
    QuestionJudgment,
    RankHit,
    RecallCount,
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


def score_relevance_audit(
    judgments: list[QuestionJudgment],
    run: EvaluationRun,
    results_file: str,
) -> ModelRecallScore:
    """Score one retrieval run without treating review-only chunks as relevant."""

    by_id = {judgment.question_id: judgment for judgment in judgments}
    result_ids = [result.question_id for result in run.results]
    if set(by_id) != set(result_ids):
        raise ValueError("judgment question ids must match the evaluation run")

    questions: dict[str, RankHit] = {}
    excluded: list[str] = []
    hits = {1: 0, 3: 0, 5: 0}
    eligible = 0
    for result in run.results:
        judgment = by_id[result.question_id]
        verified = {
            chunk.chunk_id
            for chunk in judgment.chunks
            if chunk.status == "verified"
        }
        documented = {
            chunk.chunk_id
            for chunk in judgment.chunks
            if chunk.status == "documented_sense"
        }
        ranked = {
            1: [hit.chunk_id for hit in result.top_1],
            3: [hit.chunk_id for hit in result.top_3],
            5: [hit.chunk_id for hit in result.top_5],
        }
        matched = [
            chunk_id
            for chunk_id in ranked[5]
            if chunk_id in verified
        ]
        flags = {
            cutoff: any(chunk_id in verified for chunk_id in ranked[cutoff])
            for cutoff in (1, 3, 5)
        }
        if judgment.metric_eligible:
            eligible += 1
            for cutoff in (1, 3, 5):
                hits[cutoff] += int(flags[cutoff])
        else:
            excluded.append(judgment.question_id)
        questions[result.question_id] = RankHit(
            top_1=flags[1],
            top_3=flags[3],
            top_5=flags[5],
            matched_verified_chunk_ids=matched,
            documented_sense_chunk_ids_in_top_5=[
                chunk_id for chunk_id in ranked[5] if chunk_id in documented
            ],
        )

    eligible_count = RecallCount(hits=eligible, eligible=eligible)
    return ModelRecallScore(
        model_name=run.model_name,
        results_file=results_file,
        question_count=len(run.results),
        metric_eligible_count=eligible,
        excluded_question_ids=excluded,
        recall_at_1=RecallCount(hits=hits[1], eligible=eligible_count.eligible),
        recall_at_3=RecallCount(hits=hits[3], eligible=eligible_count.eligible),
        recall_at_5=RecallCount(hits=hits[5], eligible=eligible_count.eligible),
        questions=questions,
    )


def write_evaluation(run: EvaluationRun, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(run.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
