"""Deterministic retrieval evaluation runner without answer generation."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from app.preparation.retrieval_units import parent_chunk_id
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


def collapse_units_to_parents(unit_ids: Sequence[str], width: int = 5) -> list[str]:
    """Keep the first unique parent of each ranked retrieval unit."""
    parents: list[str] = []
    seen: set[str] = set()
    for unit_id in unit_ids:
        parent_id = parent_chunk_id(unit_id)
        if parent_id in seen:
            continue
        seen.add(parent_id)
        parents.append(parent_id)
        if len(parents) == width:
            break
    return parents


def parent_recall_flags(
    parent_ids: Sequence[str],
    relevant_parent_ids: Sequence[str],
) -> dict[str, bool | int | None]:
    """Score one question with the frozen parent-collapse rule.

    A cutoff is a hit when any approved relevant parent appears inside it.
    The first relevant rank is the 1-based position in the collapsed parent
    list, or null when none of those parents were retrieved.
    """
    relevant = set(relevant_parent_ids)
    first_rank = next(
        (index for index, parent_id in enumerate(parent_ids, start=1) if parent_id in relevant),
        None,
    )
    return {
        "first_relevant_parent_rank": first_rank,
        "top_1": first_rank is not None and first_rank <= 1,
        "top_3": first_rank is not None and first_rank <= 3,
        "top_5": first_rank is not None and first_rank <= 5,
    }


def score_parent_recall(
    questions: Sequence[Mapping[str, object]],
    parents_by_question: Mapping[str, Sequence[str]],
) -> dict[str, object]:
    """Apply the frozen 14-question Recall@K rule to collapsed parent lists."""
    rows: list[dict[str, object]] = []
    hits = {1: 0, 3: 0, 5: 0}
    eligible = 0
    for question in questions:
        question_id = str(question["question_id"])
        metric_eligible = bool(question["metric_eligible"])
        raw_relevant = question["relevant_chunk_ids"]
        if not isinstance(raw_relevant, list):
            raise TypeError("relevant_chunk_ids must be a list")
        relevant = [str(chunk_id) for chunk_id in raw_relevant]
        parents = list(parents_by_question[question_id])
        flags = parent_recall_flags(parents, relevant)
        if metric_eligible:
            eligible += 1
            for cutoff in hits:
                if flags[f"top_{cutoff}"]:
                    hits[cutoff] += 1
        rows.append(
            {
                "question_id": question_id,
                "category": question.get("category", question.get("question_type")),
                "metric_eligible": metric_eligible,
                "exclusion_reason": question.get("exclusion_reason"),
                "relevant_chunk_ids": relevant,
                "parent_ids": parents,
                **flags,
            }
        )
    return {
        "eligible": eligible,
        "hits": hits,
        "questions": rows,
        "misses_at_5": [
            row["question_id"]
            for row in rows
            if row["metric_eligible"] and not row["top_5"]
        ],
    }
