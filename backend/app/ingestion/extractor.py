"""Extract text from text-based PDFs with PyMuPDF."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Callable

import pymupdf

from app.ingestion.ocr import OcrError, ocr_page
from app.ingestion.schemas import ExtractedDocument, PageText

EXTRACTION_METHOD = "pymupdf"
OUTPUT_ENCODING = "utf-8"
MIN_VISIBLE_CHARACTERS = 4
MAX_BAD_CHARACTER_RATIO = 0.01

PageOcr = Callable[[pymupdf.Page], str]


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


def normalize_text(text: str) -> str:
    """Normalize layout whitespace without rewriting recognized characters."""
    normalized = unicodedata.normalize("NFC", text).replace("\r\n", "\n")
    normalized = normalized.replace("\r", "\n").replace("\u00a0", " ")
    lines = [line.rstrip() for line in normalized.splitlines()]
    return "\n".join(lines).strip()


def is_text_usable(text: str) -> bool:
    """Return whether extracted text is safe to use without OCR.

    Legacy font mappings commonly produce C0/C1 controls, replacement
    characters, private-use characters, and symbol-heavy output. Blank or
    extremely sparse text is also sent to OCR.
    """
    visible = [character for character in text if not character.isspace()]
    if len(visible) < MIN_VISIBLE_CHARACTERS:
        return False

    bad_characters = 0
    letters_or_numbers = 0
    symbols = 0
    for character in visible:
        category = unicodedata.category(character)
        if (
            character == "\ufffd"
            or 0x80 <= ord(character) <= 0x9F
            or category in {"Cc", "Cs", "Co", "Cn"}
        ):
            bad_characters += 1
        if category[0] in {"L", "N"}:
            letters_or_numbers += 1
        if category[0] == "S":
            symbols += 1

    if bad_characters / len(visible) > MAX_BAD_CHARACTER_RATIO:
        return False
    if letters_or_numbers / len(visible) < 0.35:
        return False
    if symbols / len(visible) > 0.20:
        return False
    return True


def _document_method(pages: list[PageText]) -> str:
    methods = {page.extraction_method for page in pages}
    if len(methods) == 1:
        return methods.pop()
    return "mixed"


def extract_pdf(
    source: Path,
    filename: str,
    ocr_engine: PageOcr | None = None,
) -> ExtractedDocument:
    original_hash = _sha256(source)
    run_ocr = ocr_engine or ocr_page
    try:
        with pymupdf.open(source) as document:
            if document.needs_pass:
                raise IngestionError(
                    f"'{filename}' is encrypted and cannot be extracted."
                )

            pages: list[PageText] = []
            for index, page in enumerate(document, start=1):
                try:
                    pymupdf_text = page.get_text("text")
                except Exception as exc:
                    raise IngestionError(
                        f"Could not extract text from page {index} of '{filename}'."
                    ) from exc
                if not isinstance(pymupdf_text, str):
                    raise IngestionError(
                        f"Page {index} of '{filename}' did not return text."
                    )

                if is_text_usable(pymupdf_text):
                    raw_text = pymupdf_text
                    method = "pymupdf"
                else:
                    try:
                        raw_text = run_ocr(page)
                    except OcrError as exc:
                        raise IngestionError(
                            f"OCR failed on page {index} of '{filename}': {exc}"
                        ) from exc
                    except Exception as exc:
                        raise IngestionError(
                            f"OCR failed on page {index} of '{filename}'."
                        ) from exc
                    if not isinstance(raw_text, str):
                        raise IngestionError(
                            f"OCR did not return text for page {index} "
                            f"of '{filename}'."
                        )
                    method = "ocr"

                pages.append(
                    PageText(
                        page_number=index,
                        text=normalize_text(raw_text),
                        extraction_method=method,
                        raw_text=raw_text,
                        pymupdf_text=pymupdf_text,
                    )
                )
    except IngestionError:
        raise
    except Exception as exc:
        raise IngestionError(f"Could not open '{filename}': {exc}") from exc

    if _sha256(source) != original_hash:
        raise IngestionError(f"Original PDF was modified: {filename}")

    return ExtractedDocument(
        filename=filename,
        page_count=len(pages),
        extraction_method=_document_method(pages),
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
    ocr_engine: PageOcr | None = None,
) -> tuple[ExtractedDocument, Path]:
    source_directory = (source_dir or raw_dir()).resolve()
    destination_directory = (output_dir or extracted_dir()).resolve()
    source = resolve_raw_pdf(filename, source_directory)
    relative_name = source.relative_to(source_directory).as_posix()
    document = extract_pdf(source, relative_name, ocr_engine)
    output_path = save_extraction(
        document, source, source_directory, destination_directory
    )
    return document, output_path
