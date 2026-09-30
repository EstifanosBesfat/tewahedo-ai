"""Extract a text-based PDF from data/raw into data/extracted.

Run from the backend directory:

    py -3 scripts/extract_pdf.py book.pdf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.extractor import IngestionError, ingest_pdf


def emit(stream, message: str) -> None:
    line = (message + "\n").encode("utf-8", errors="replace")
    buffer = getattr(stream, "buffer", None)
    if buffer is None:
        stream.write(message + "\n")
        return
    buffer.write(line)
    buffer.flush()


def run(
    filename: str,
    source_dir: Path | None = None,
    output_dir: Path | None = None,
) -> int:
    try:
        document, output_path = ingest_pdf(filename, source_dir, output_dir)
    except IngestionError as exc:
        emit(sys.stderr, f"error: {exc}")
        return 1

    emit(
        sys.stdout,
        f"{document.page_count} pages -> {output_path}",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Extract text from a PDF stored in data/raw/."
    )
    parser.add_argument(
        "filename",
        help="PDF filename inside data/raw/, for example book.pdf",
    )
    args = parser.parse_args(argv)
    return run(args.filename)


if __name__ == "__main__":
    raise SystemExit(main())
