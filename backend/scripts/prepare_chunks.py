"""Prepare extracted page text as semantic chunks for manual review.

Run from the backend directory:

    py -3 scripts/prepare_chunks.py 10commandments.pdf
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.preparation.chunker import load_and_prepare
from app.preparation.schemas import ChunkingConfig

EXTRACTED_DIR = BACKEND_ROOT / "data" / "extracted"
PROCESSED_DIR = BACKEND_ROOT / "data" / "processed"


def emit(stream, message: str) -> None:
    line = (message + "\n").encode("utf-8", errors="replace")
    buffer = getattr(stream, "buffer", None)
    if buffer is None:
        stream.write(message + "\n")
        return
    buffer.write(line)
    buffer.flush()


def _input_path(filename: str, source_dir: Path) -> Path:
    supplied = Path(filename)
    if supplied.name != filename:
        raise ValueError("filename must not contain a directory")
    json_name = supplied.with_suffix(".json").name
    path = source_dir / json_name
    if not path.is_file():
        raise ValueError(f"extracted JSON not found: {path}")
    return path


def run(
    filename: str,
    target_chars: int = 1200,
    overlap_chars: int = 150,
    source_dir: Path | None = None,
    output_dir: Path | None = None,
) -> int:
    selected_source_dir = source_dir or EXTRACTED_DIR
    selected_output_dir = output_dir or PROCESSED_DIR
    try:
        input_path = _input_path(filename, selected_source_dir)
        config = ChunkingConfig(
            target_chars=target_chars,
            overlap_chars=overlap_chars,
        )
        document = load_and_prepare(input_path, config)
        selected_output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (
            selected_output_dir / f"{input_path.stem}.chunks.json"
        )
        output_path.write_text(
            json.dumps(
                document.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        emit(sys.stderr, f"error: {exc}")
        return 1

    emit(sys.stdout, f"{document.chunk_count} chunks -> {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Prepare extracted Amharic text as semantic chunks."
    )
    parser.add_argument(
        "filename",
        help="Extracted JSON or source PDF filename, for example book.pdf",
    )
    parser.add_argument(
        "--target-chars",
        type=int,
        default=1200,
        help="Desired maximum chunk size in characters (default: 1200)",
    )
    parser.add_argument(
        "--overlap-chars",
        type=int,
        default=150,
        help="Maximum trailing overlap in characters (default: 150)",
    )
    args = parser.parse_args(argv)
    return run(args.filename, args.target_chars, args.overlap_chars)


if __name__ == "__main__":
    raise SystemExit(main())
