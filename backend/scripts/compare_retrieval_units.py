"""Score refined retrieval units against the frozen relevance audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.preparation.retrieval_units import (  # noqa: E402
    E5_TOKEN_LIMIT,
    parent_chunk_id,
)
from app.preparation.schemas import (  # noqa: E402
    PreparedDocument,
    RetrievalUnitDocument,
)
from app.retrieval.evaluation import score_relevance_audit  # noqa: E402
from app.retrieval.runtime import create_e5_service  # noqa: E402
from app.retrieval.schemas import (  # noqa: E402
    EvaluationQuestionSet,
    EvaluationResult,
    EvaluationRun,
    RetrievalAudit,
    SearchResult,
)

DEFAULT_QUESTIONS = (
    BACKEND_ROOT / "data" / "evaluation" / "amharic_retrieval_questions.json"
)
DEFAULT_AUDIT = BACKEND_ROOT / "data" / "evaluation" / "retrieval-audit.json"
DEFAULT_CHUNKS = (
    BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
)
DEFAULT_UNITS = (
    BACKEND_ROOT / "data" / "processed" / "10commandments.retrieval-units.json"
)
DEFAULT_STORE = (
    BACKEND_ROOT / "data" / "vectorstore" / "multilingual-e5-small-units"
)
DEFAULT_REPORT = (
    BACKEND_ROOT / "data" / "evaluation" / "retrieval-unit-comparison.json"
)
BASELINE_RECALL = {"recall_at_1": "5/14", "recall_at_3": "9/14", "recall_at_5": "12/14"}


def _collapse_to_parents(run: EvaluationRun, width: int) -> EvaluationRun:
    results: list[EvaluationResult] = []
    for result in run.results:
        seen: set[str] = set()
        parents: list[SearchResult] = []
        for hit in result.top_5:
            parent_id = parent_chunk_id(hit.chunk_id)
            if parent_id in seen:
                continue
            seen.add(parent_id)
            parents.append(hit.model_copy(update={"chunk_id": parent_id}))
            if len(parents) == width:
                break
        results.append(
            result.model_copy(
                update={
                    "top_1": parents[:1],
                    "top_3": parents[:3],
                    "top_5": parents[:5],
                }
            )
        )
    return run.model_copy(update={"results": results})


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Compare refined-unit retrieval with the E5-small audit."
    )
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--units", type=Path, default=DEFAULT_UNITS)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--parent-width", type=int, default=5)
    args = parser.parse_args(argv)

    prepared = PreparedDocument.model_validate_json(
        args.chunks.read_text(encoding="utf-8")
    )
    units = RetrievalUnitDocument.model_validate_json(
        args.units.read_text(encoding="utf-8")
    )
    audit = RetrievalAudit.model_validate_json(
        args.audit.read_text(encoding="utf-8")
    )
    questions = EvaluationQuestionSet.model_validate_json(
        args.questions.read_text(encoding="utf-8")
    )
    service = create_e5_service(args.store, args.device, args.model_dir)
    gathered: list[EvaluationResult] = []
    for item in questions.questions:
        ranked = service.search(item.question, top_k=args.parent_width * 4)
        gathered.append(
            EvaluationResult(
                question_id=item.question_id,
                category=item.category,
                question=item.question,
                review_focus=item.review_focus,
                top_1=ranked[:1],
                top_3=ranked[:3],
                top_5=ranked,
            )
        )
    unit_run = EvaluationRun(
        model_name=service.embedding_provider.model_name,
        collection_name=service.vector_store.collection_name,
        question_count=len(gathered),
        results=gathered,
    )
    parent_run = _collapse_to_parents(unit_run, args.parent_width)
    score = score_relevance_audit(
        audit.judgments,
        parent_run,
        "10commandments.retrieval-units.json",
    )
    lengths = [unit.token_length for unit in units.units]
    old_lengths = service.embedding_provider.document_token_lengths(
        [chunk.text for chunk in prepared.chunks]
    )
    old_cross = sum(
        chunk.page_start != chunk.page_end for chunk in prepared.chunks
    )
    new_cross = sum(unit.page_start != unit.page_end for unit in units.units)

    def _length_summary(values: list[int]) -> dict[str, int | float]:
        return {
            "minimum": min(values),
            "maximum": max(values),
            "average": round(sum(values) / len(values), 1),
            "exceeding_e5_limit": sum(value > E5_TOKEN_LIMIT for value in values),
        }

    report = {
        "model_name": score.model_name,
        "old_chunk_count": len(prepared.chunks),
        "new_retrieval_chunk_count": units.unit_count,
        "old_token_length": _length_summary(old_lengths),
        "new_token_length": _length_summary(lengths),
        "e5_token_limit": E5_TOKEN_LIMIT,
        "safety_limit": units.max_tokens,
        "old_page_crossing_chunks": old_cross,
        "new_page_crossing_chunks": new_cross,
        "parent_rankings": {
            result.question_id: [hit.chunk_id for hit in result.top_5]
            for result in parent_run.results
        },
        "baseline_recall": BASELINE_RECALL,
        "refined_recall": {
            "eligible_questions": score.metric_eligible_count,
            "question_count": score.question_count,
            "excluded_question_ids": score.excluded_question_ids,
            "recall_at_1": f"{score.recall_at_1.hits}/{score.recall_at_1.eligible}",
            "recall_at_3": f"{score.recall_at_3.hits}/{score.recall_at_3.eligible}",
            "recall_at_5": f"{score.recall_at_5.hits}/{score.recall_at_5.eligible}",
        },
        "questions": {
            question_id: hit.model_dump(mode="json")
            for question_id, hit in score.questions.items()
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"units={units.unit_count} "
        f"recall={report['refined_recall']['recall_at_1']} "
        f"{report['refined_recall']['recall_at_3']} "
        f"{report['refined_recall']['recall_at_5']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
