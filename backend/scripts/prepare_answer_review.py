"""Write the human-review packet for the frozen answer evaluation.

The script reads the existing answer-evaluation dataset, ground truth, and
parent chunks. It writes a packet, a pending review input, a reviewed
dataset, and a report. It does not replace the answer-evaluation files.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.answers.passages import ParentCorpus
from app.answers.review import (
    ReviewInput,
    apply_answer_reviews,
    build_review_worksheet,
    load_expected_concepts,
    load_ground_truth_questions,
    load_review_input,
    pending_submissions,
    render_review_packet,
    sha256_file,
    write_review_outputs,
)
from app.answers.schemas import AnswerEvaluationDataset

EVALUATION = BACKEND_ROOT / "data" / "evaluation"
ANSWER_DATASET = EVALUATION / "answer-evaluation-bge-m3.json"
GROUND_TRUTH = EVALUATION / "ground-truth-v3.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
PACKET_PATH = EVALUATION / "answer-review-packet-bge-m3.md"
INPUT_PATH = EVALUATION / "answer-review-input-bge-m3.json"
REVIEWED_PATH = EVALUATION / "answer-review-bge-m3.json"
REPORT_PATH = EVALUATION / "answer-review-bge-m3-report.md"


def main() -> None:
    dataset = AnswerEvaluationDataset.model_validate_json(
        ANSWER_DATASET.read_text(encoding="utf-8")
    )
    worksheet = build_review_worksheet(
        dataset,
        load_expected_concepts(GROUND_TRUTH),
        load_ground_truth_questions(GROUND_TRUTH),
        ParentCorpus.load(CORPUS_PATH),
    )
    write_input = not INPUT_PATH.exists()
    if write_input:
        review_input = ReviewInput(schema_version="1", reviews=pending_submissions(worksheet))
    else:
        review_input = load_review_input(INPUT_PATH)
    reviewed = apply_answer_reviews(
        worksheet,
        review_input.reviews,
        source_name=str(ANSWER_DATASET),
        source_sha256=sha256_file(ANSWER_DATASET),
        ground_truth_file=str(GROUND_TRUTH),
        corpus_file=str(CORPUS_PATH),
    )
    write_review_outputs(
        render_review_packet(worksheet),
        review_input,
        reviewed,
        PACKET_PATH,
        INPUT_PATH,
        REVIEWED_PATH,
        REPORT_PATH,
        write_input=write_input,
    )
    print(f"wrote {PACKET_PATH}")
    print(f"{'wrote' if write_input else 'kept'} {INPUT_PATH}")
    print(f"wrote {REVIEWED_PATH}")
    print(f"wrote {REPORT_PATH}")
    print(f"questions {reviewed.question_count}")


if __name__ == "__main__":
    main()
