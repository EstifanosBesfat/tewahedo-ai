"""Generate a four-question Groq sample from live BGE-M3 retrieval.

The output is a new evaluation file. Frozen retrieval, ground-truth, and
review files are not written.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.answers.groq import GroqConfigError, groq_provider_from_env
from app.answers.groq_sample import (
    configuration_failure_sample,
    load_sample_questions,
    run_groq_sample,
    write_groq_sample,
)
from app.answers.passages import ParentCorpus, passages_from_search_results
from app.retrieval.runtime import create_bge_m3_service

QUESTIONS_PATH = BACKEND_ROOT / "data" / "evaluation" / "amharic_retrieval_questions.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
OUTPUT_JSON = BACKEND_ROOT / "data" / "evaluation" / "groq-answer-sample.json"
OUTPUT_REPORT = BACKEND_ROOT / "data" / "evaluation" / "groq-answer-sample-report.md"


def main() -> None:
    questions = load_sample_questions(QUESTIONS_PATH)
    try:
        provider = groq_provider_from_env()
    except GroqConfigError as exc:
        payload = configuration_failure_sample(questions, exc.code, str(exc))
        write_groq_sample(payload, OUTPUT_JSON, OUTPUT_REPORT)
        print(str(exc))
        print(f"wrote {OUTPUT_JSON}")
        return
    corpus = ParentCorpus.load(CORPUS_PATH)
    service = create_bge_m3_service()

    def retrieve(question: str):
        return passages_from_search_results(service.search(question, top_k=20), corpus)

    payload = run_groq_sample(
        questions,
        retrieve,
        provider.generate,
        provider.model_name,
    )
    write_groq_sample(payload, OUTPUT_JSON, OUTPUT_REPORT)
    print(f"wrote {OUTPUT_JSON}")
    print(f"wrote {OUTPUT_REPORT}")
    print(f"model {provider.model_name}")


if __name__ == "__main__":
    main()
