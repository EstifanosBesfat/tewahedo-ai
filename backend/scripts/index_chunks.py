"""Index prepared chunks with multilingual E5-small and persistent Chroma."""

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

DEFAULT_CHUNKS_PATH = (
    BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Index prepared chunks with multilingual E5-small."
    )
    parser.add_argument(
        "--chunks",
        type=Path,
        default=DEFAULT_CHUNKS_PATH,
        help="Prepared chunk JSON path",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_VECTOR_STORE_PATH,
        help="Persistent Chroma directory",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Sentence Transformers device, for example cpu or cuda",
    )
    args = parser.parse_args(argv)

    try:
        service = create_e5_service(args.store, args.device)
        report = service.index_document(args.chunks)
    except (OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            report.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
