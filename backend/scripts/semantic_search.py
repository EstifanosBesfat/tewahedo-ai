"""Search the local multilingual E5 Chroma collection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.retrieval.runtime import (
    DEFAULT_VECTOR_STORE_PATH,
    create_e5_service,
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Run semantic search over indexed Amharic chunks."
    )
    parser.add_argument("query", help="Non-empty Amharic search query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_VECTOR_STORE_PATH,
    )
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)

    try:
        service = create_e5_service(args.store, args.device)
        results = service.search(args.query, args.top_k)
    except (OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            [result.model_dump(mode="json") for result in results],
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
