"""Score the existing 182-unit E5 index against ground-truth-v2.

Uses the same search path as scripts/compare_retrieval_units.py:
query text is stripped, embedded with the E5 query prefix, and the top 20
units are collapsed to five unique parent chunks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.preparation.retrieval_units import parent_chunk_id
from app.retrieval.runtime import create_e5_service

EVAL_DIR = BACKEND_ROOT / "data" / "evaluation"
STORE = BACKEND_ROOT / "data" / "vectorstore" / "multilingual-e5-small-units"
PARENT_WIDTH = 5
SEARCH_WIDTH = PARENT_WIDTH * 4

questions = json.loads(
    (EVAL_DIR / "amharic_retrieval_questions.json").read_text(encoding="utf-8")
)
ground_truth = json.loads(
    (EVAL_DIR / "ground-truth-v2.json").read_text(encoding="utf-8")
)
previous = json.loads(
    (EVAL_DIR / "retrieval-unit-comparison.json").read_text(encoding="utf-8")
)
by_truth = {item["question_id"]: item for item in ground_truth["questions"]}
previous_flags = previous["questions"]
previous_parents = previous["parent_rankings"]

MODEL_DIR = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--intfloat--multilingual-e5-small"
    / "snapshots"
    / "614241f622f53c4eeff9890bdc4f31cfecc418b3"
)
service = create_e5_service(STORE, "cpu", MODEL_DIR)
unit_count = service.vector_store.count
if unit_count != 182:
    raise SystemExit(f"expected 182 retrieval units, found {unit_count}")

question_results = []
hits = {1: 0, 3: 0, 5: 0}
for item in questions["questions"]:
    truth = by_truth[item["question_id"]]
    if truth["question"] != item["question"]:
        raise SystemExit(f"question text drifted for {item['question_id']}")
    ranked = service.search(item["question"], top_k=SEARCH_WIDTH)
    units = []
    parents: list[str] = []
    seen: set[str] = set()
    for index, hit in enumerate(ranked, start=1):
        parent_id = parent_chunk_id(hit.chunk_id)
        units.append(
            {
                "rank": index,
                "unit_id": hit.chunk_id,
                "parent_chunk_id": parent_id,
                "page_start": hit.page_start,
                "page_end": hit.page_end,
                "similarity_score": hit.similarity_score,
            }
        )
        if parent_id not in seen:
            seen.add(parent_id)
            parents.append(parent_id)
    parents = parents[:PARENT_WIDTH]
    relevant = set(truth["relevant_chunk_ids"])
    flags = {
        cutoff: any(chunk_id in relevant for chunk_id in parents[:cutoff])
        for cutoff in (1, 3, 5)
    }
    matched = [chunk_id for chunk_id in parents if chunk_id in relevant]
    if truth["metric_eligible"]:
        for cutoff in (1, 3, 5):
            hits[cutoff] += int(flags[cutoff])
    old = previous_flags[item["question_id"]]
    old_flags = {
        "top_1": old["top_1"],
        "top_3": old["top_3"],
        "top_5": old["top_5"],
    }
    new_flags = {
        "top_1": flags[1],
        "top_3": flags[3],
        "top_5": flags[5],
    }
    if not truth["metric_eligible"]:
        change = "excluded"
    elif new_flags == old_flags:
        change = "unchanged"
    elif all(
        (not old_flags[key]) or new_flags[key]
        for key in ("top_1", "top_3", "top_5")
    ) and any(
        new_flags[key] and not old_flags[key]
        for key in ("top_1", "top_3", "top_5")
    ):
        change = "improved"
    elif any(
        old_flags[key] and not new_flags[key]
        for key in ("top_1", "top_3", "top_5")
    ):
        change = "worsened"
    else:
        change = "unchanged"
    question_results.append(
        {
            "question_id": item["question_id"],
            "question": item["question"],
            "metric_eligible": truth["metric_eligible"],
            "expected_concept": truth["expected_concept"],
            "relevant_chunk_ids": truth["relevant_chunk_ids"],
            "top_1": flags[1],
            "top_3": flags[3],
            "top_5": flags[5],
            "matched_relevant_parent_ids": matched,
            "parent_ranking": [
                {"rank": index, "parent_chunk_id": chunk_id}
                for index, chunk_id in enumerate(parents, start=1)
            ],
            "unit_ranking": units,
            "previous_provisional": old_flags,
            "previous_parent_ranking": previous_parents[item["question_id"]],
            "parent_ranking_unchanged": previous_parents[item["question_id"]]
            == parents,
            "change_vs_provisional": change,
        }
    )

eligible_results = [
    result for result in question_results if result["metric_eligible"]
]
report = {
    "benchmark": "ground-truth-v2",
    "model_name": service.embedding_provider.model_name,
    "collection_name": service.vector_store.collection_name,
    "unit_count": unit_count,
    "retrieval_settings": {
        "store": "backend/data/vectorstore/multilingual-e5-small-units",
        "query_processing": "strip whitespace, then the existing E5 query prefix",
        "search_top_k_before_parent_collapse": SEARCH_WIDTH,
        "parent_width": PARENT_WIDTH,
        "denominator": 14,
    },
    "previous_provisional_recall": {
        "recall_at_1": "7/14",
        "recall_at_3": "10/14",
        "recall_at_5": "12/14",
    },
    "recall_at_1": f"{hits[1]}/14",
    "recall_at_3": f"{hits[3]}/14",
    "recall_at_5": f"{hits[5]}/14",
    "excluded_question_ids": ["direct-01"],
    "misses_at_5": [
        result["question_id"]
        for result in eligible_results
        if not result["top_5"]
    ],
    "improved": [
        result["question_id"]
        for result in eligible_results
        if result["change_vs_provisional"] == "improved"
    ],
    "worsened": [
        result["question_id"]
        for result in eligible_results
        if result["change_vs_provisional"] == "worsened"
    ],
    "questions": question_results,
}
output = EVAL_DIR / "retrieval-evaluation-v2.json"
output.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(
    f"units={unit_count} recall={report['recall_at_1']} "
    f"{report['recall_at_3']} {report['recall_at_5']}"
)
