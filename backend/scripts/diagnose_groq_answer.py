"""Run one live Groq question and write a new diagnostic file.

The original groq-answer-sample.json and frozen evaluation files are not written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.answers.dataset import assert_writable_output
from app.answers.groq import groq_provider_from_env
from app.answers.groq_sample import (
    load_sample_questions,
    render_groq_sample_report,
    run_groq_sample,
)
from app.answers.passages import ParentCorpus, passages_from_search_results
from app.retrieval.runtime import create_bge_m3_service

QUESTION_ID = "direct-02"
SNAPSHOT = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--BAAI--bge-m3"
    / "snapshots"
    / "5617a9f61b028005a4858fdac845db406aefb181"
)
QUESTIONS_PATH = BACKEND_ROOT / "data" / "evaluation" / "amharic_retrieval_questions.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
OUTPUT_JSON = BACKEND_ROOT / "data" / "evaluation" / "groq-answer-diagnostic-top3.json"
OUTPUT_REPORT = BACKEND_ROOT / "data" / "evaluation" / "groq-answer-diagnostic-top3-report.md"


def main() -> None:
    if OUTPUT_JSON.name == "groq-answer-sample.json":
        raise RuntimeError("diagnostic output must not replace the original sample")
    assert_writable_output(OUTPUT_JSON)
    assert_writable_output(OUTPUT_REPORT)
    questions = [
        question
        for question in load_sample_questions(QUESTIONS_PATH)
        if question["question_id"] == QUESTION_ID
    ]
    provider = groq_provider_from_env()
    corpus = ParentCorpus.load(CORPUS_PATH)
    service = create_bge_m3_service(model_path=SNAPSHOT)

    def retrieve(question: str):
        return passages_from_search_results(service.search(question, top_k=20), corpus)

    payload = run_groq_sample(
        questions,
        retrieve,
        provider.generate,
        provider.model_name,
    )
    payload["description"] = "One controlled Groq question with a three-passage token budget."
    payload["token_estimate"] = provider.last_token_estimate
    payload["prompt_passage_ids"] = provider.last_prompt_passage_ids
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    OUTPUT_REPORT.write_text(render_groq_sample_report(payload), encoding="utf-8")
    record = payload["records"][0]
    print(f"question {record['question_id']}")
    print(f"model {provider.model_name}")
    print(f"status {record['generation_status']}")
    print(f"error_code {record['error_code']}")
    print(f"latency {record['latency_seconds']}")
    print(f"token_estimate {provider.last_token_estimate}")
    print(f"prompt_passages {','.join(provider.last_prompt_passage_ids)}")
    print(f"wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
