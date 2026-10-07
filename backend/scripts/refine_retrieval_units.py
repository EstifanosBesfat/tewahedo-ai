"""Derive token-bounded retrieval units from the prepared chunks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.preparation.retrieval_units import (  # noqa: E402
    DEFAULT_MAX_TOKENS,
    refine_prepared_document,
)
from app.preparation.schemas import (  # noqa: E402
    ChunkingConfig,
    PreparedChunk,
    PreparedDocument,
)

DEFAULT_CHUNKS = (
    BACKEND_ROOT / "data" / "processed" / "10commandments.chunks.json"
)
DEFAULT_EXTRACTED = BACKEND_ROOT / "data" / "extracted" / "10commandments.json"
DEFAULT_UNITS = (
    BACKEND_ROOT / "data" / "processed" / "10commandments.retrieval-units.json"
)
DEFAULT_PREPARED = (
    BACKEND_ROOT
    / "data"
    / "processed"
    / "10commandments.retrieval-units.prepared.json"
)


def e5_token_length(tokenizer: object, text: str) -> int:
    prefixed = f"passage: {text}"
    encoded = tokenizer(  # type: ignore[operator]
        prefixed,
        add_special_tokens=True,
        truncation=False,
    )
    return len(encoded["input_ids"])


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Split prepared chunks into focused retrieval units."
    )
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--extracted", type=Path, default=DEFAULT_EXTRACTED)
    parser.add_argument("--units", type=Path, default=DEFAULT_UNITS)
    parser.add_argument("--prepared", type=Path, default=DEFAULT_PREPARED)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    args = parser.parse_args(argv)

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir,
        local_files_only=True,
    )
    document = PreparedDocument.model_validate_json(
        args.chunks.read_text(encoding="utf-8")
    )
    extracted = json.loads(args.extracted.read_text(encoding="utf-8"))
    page_text = {
        int(page["page_number"]): str(page.get("text", ""))
        for page in extracted["pages"]
    }
    units = refine_prepared_document(
        document,
        lambda text: e5_token_length(tokenizer, text),
        max_tokens=args.max_tokens,
        page_text=page_text,
    )
    prepared = PreparedDocument(
        document_id=document.document_id,
        source_filename=document.source_filename,
        source_page_count=document.source_page_count,
        chunking=ChunkingConfig(target_chars=900, overlap_chars=0),
        chunk_count=units.unit_count,
        chunks=[
            PreparedChunk(
                chunk_id=unit.chunk_id,
                document_id=unit.document_id,
                page_start=unit.page_start,
                page_end=unit.page_end,
                text=unit.text,
                extraction_method=unit.extraction_method,
                source_quality_score=unit.source_quality_score,
            )
            for unit in units.units
        ],
    )
    args.units.parent.mkdir(parents=True, exist_ok=True)
    args.units.write_text(
        json.dumps(units.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    args.prepared.write_text(
        json.dumps(prepared.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    lengths = [unit.token_length for unit in units.units]
    print(
        json.dumps(
            {
                "parent_chunks": units.parent_chunk_count,
                "retrieval_units": units.unit_count,
                "min_tokens": min(lengths),
                "max_tokens": max(lengths),
                "average_tokens": round(sum(lengths) / len(lengths), 1),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
