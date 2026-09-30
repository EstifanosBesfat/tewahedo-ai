"""Extract text from text-based PDFs with PyMuPDF."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz

from app.ingestion.schemas import ExtractedDocument, PageText

EXTRACTION_METHOD = "pymupdf"
OUTPUT_ENCODING = "utf-8"


class IngestionError(Exception):
    """Raised when a PDF in data/raw cannot be ingested."""


def backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def raw_dir() -> Path:
    return backend_root() / "data" / "raw"


def extracted_dir() -> Path:
    return backend_root() / "data" / "extracted"


def resolve_raw_pdf(filename: str, source_dir: Path | None = None) -> Path:
    if not isinstance(filename, str) or not filename.strip():
        raise IngestionError("A PDF filename inside data/raw is required.")

    source_directory = (source_dir or raw_dir()).resolve()
    requested = Path(filename)
    if requested.is_absolute():
        raise IngestionError("Pass a filename inside data/raw, not an absolute path.")

    try:
        candidate = (source_directory / requested).resolve()
    except OSError as exc:
        raise IngestionError(f"Invalid PDF filename: {filename}") from exc

    if not candidate.is_relative_to(source_directory):
        raise IngestionError("The PDF must stay inside data/raw.")
    if candidate.suffix.lower() != ".pdf":
        raise IngestionError("Only .pdf files can be extracted.")
    if not candidate.is_file():
        raise IngestionError(f"PDF not found in data/raw: {filename}")
    return candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pdf(source: Path, filename: str) -> ExtractedDocument:
    original_hash = _sha256(source)
    try:
        with fitz.open(source) as document:
            if document.needs_pass:
                raise IngestionError(
                    f"'{filename}' is encrypted and cannot be extracted."
                )

            pages: list[PageText] = []
            for index, page in enumerate(document, start=1):
                try:
                    text = page.get_text("text")
                except Exception as exc:
                    raise IngestionError(
                        f"Could not extract text from page {index} of '{filename}'."
                    ) from exc
                if not isinstance(text, str):
                    raise IngestionError(
                        f"Page {index} of '{filename}' did not return text."
                    )
                pages.append(PageText(page_number=index, text=text))
    except IngestionError:
        raise
    except Exception as exc:
        raise IngestionError(f"Could not open '{filename}': {exc}") from exc

    if _sha256(source) != original_hash:
        raise IngestionError(f"Original PDF was modified: {filename}")

    return ExtractedDocument(
        filename=filename,
        page_count=len(pages),
        extraction_method=EXTRACTION_METHOD,
        encoding=OUTPUT_ENCODING,
        pages=pages,
    )


def save_extraction(
    document: ExtractedDocument,
    source: Path,
    source_dir: Path,
    output_dir: Path,
) -> Path:
    relative = source.resolve().relative_to(source_dir.resolve())
    destination = (output_dir / relative).with_suffix(".json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document.model_dump(), ensure_ascii=False, indent=2) + "\n"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(payload, encoding=OUTPUT_ENCODING)
    temporary.replace(destination)
    return destination


def ingest_pdf(
    filename: str,
    source_dir: Path | None = None,
    output_dir: Path | None = None,
) -> tuple[ExtractedDocument, Path]:
    source_directory = (source_dir or raw_dir()).resolve()
    destination_directory = (output_dir or extracted_dir()).resolve()
    source = resolve_raw_pdf(filename, source_directory)
    relative_name = source.relative_to(source_directory).as_posix()
    document = extract_pdf(source, relative_name)
    output_path = save_extraction(
        document, source, source_directory, destination_directory
    )
    return document, output_path
