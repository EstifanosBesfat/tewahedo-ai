"""Write the source-grounded answer evaluation for the frozen BGE-M3 run.

The script reads the existing question file, BGE-M3 rankings, and parent
chunks. It writes a new dataset and report. It does not search again and
does not modify retrieval artifacts.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.answers.dataset import build_answer_dataset, write_answer_outputs

QUESTIONS_PATH = BACKEND_ROOT / "data" / "evaluation" / "amharic_retrieval_questions.json"
RETRIEVAL_PATH = BACKEND_ROOT / "data" / "evaluation" / "retrieval-evaluation-bge-m3.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
OUTPUT_JSON = BACKEND_ROOT / "data" / "evaluation" / "answer-evaluation-bge-m3.json"
OUTPUT_REPORT = BACKEND_ROOT / "data" / "evaluation" / "answer-evaluation-bge-m3-report.md"


def main() -> None:
    dataset = build_answer_dataset(QUESTIONS_PATH, RETRIEVAL_PATH, CORPUS_PATH)
    write_answer_outputs(dataset, OUTPUT_JSON, OUTPUT_REPORT)
    print(f"wrote {OUTPUT_JSON}")
    print(f"wrote {OUTPUT_REPORT}")
    print(f"questions {dataset.question_count}")


if __name__ == "__main__":
    main()
