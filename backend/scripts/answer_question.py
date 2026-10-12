"""Answer one question from live BGE-M3 passages and Groq.

Run this from the backend directory after backend/.env contains GROQ_API_KEY
and GROQ_MODEL. The script prints the answer and citation ids. It does not
print the API key.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.answers.groq import GroqAnswerError, GroqConfigError, groq_provider_from_env
from app.answers.passages import ParentCorpus, passages_from_search_results
from app.answers.schemas import AnswerGenerationRequest
from app.retrieval.runtime import create_bge_m3_service

CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        raise SystemExit("Usage: python scripts/answer_question.py \"የጥያቄ ጽሑፍ\"")
    question = sys.argv[1].strip()
    try:
        provider = groq_provider_from_env()
    except GroqConfigError as exc:
        raise SystemExit(str(exc)) from exc
    corpus = ParentCorpus.load(CORPUS_PATH)
    service = create_bge_m3_service()
    passages = passages_from_search_results(service.search(question, top_k=20), corpus)
    try:
        answer = provider.generate(
            AnswerGenerationRequest(
                question_id="ad-hoc",
                question=question,
                language="am",
                passages=passages,
            )
        )
    except GroqAnswerError as exc:
        raise SystemExit(f"{exc.code}: {exc}") from exc
    print(f"model: {answer.model_name}")
    print(f"abstained: {answer.abstained}")
    print(answer.answer_text)
    for citation in answer.citations:
        print(
            f"citation: {citation.parent_chunk_id} "
            f"{citation.document_id} pages {citation.page_start}-{citation.page_end} "
            f"role {citation.role}"
        )


if __name__ == "__main__":
    main()
