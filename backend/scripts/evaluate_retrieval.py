"""Run the fixed 15-question retrieval evaluation and save ranked results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.retrieval.evaluation import run_evaluation, write_evaluation
from app.retrieval.runtime import (
    DEFAULT_VECTOR_STORE_PATH,
    create_e5_service,
)

DEFAULT_QUESTIONS_PATH = (
    BACKEND_ROOT
    / "data"
    / "evaluation"
    / "amharic_retrieval_questions.json"
)
DEFAULT_RESULTS_PATH = (
    BACKEND_ROOT
    / "data"
    / "evaluation"
    / "multilingual-e5-small.results.json"
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Evaluate multilingual E5 retrieval on Amharic questions."
    )
    parser.add_argument(
        "--questions",
        type=Path,
        default=DEFAULT_QUESTIONS_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULTS_PATH,
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_VECTOR_STORE_PATH,
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=None,
        help="Local model directory. Omit to load from the model hub.",
    )
    args = parser.parse_args(argv)

    try:
        service = create_e5_service(args.store, args.device, args.model_dir)
        evaluation = run_evaluation(service, args.questions)
        write_evaluation(evaluation, args.output)
    except (OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"{evaluation.question_count} questions -> {args.output}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
