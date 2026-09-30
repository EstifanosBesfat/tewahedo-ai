"""Tests for text-based PDF ingestion."""

import hashlib
import json
import os
from pathlib import Path

import pymupdf
import pytest

from app.ingestion.extractor import (
    EXTRACTION_METHOD,
    IngestionError,
    ingest_pdf,
    is_text_usable,
)
from app.main import app
from scripts.extract_pdf import run

PAGE_ONE = "ቤተ ክርስቲያን"
PAGE_TWO = "መጽሐፍ ቅዱስ"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _words(text: str) -> str:
    return " ".join(text.replace("\u00a0", " ").split())


def _ethiopic_font() -> Path:
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates = [
        windir / "Fonts" / "ebrima.ttf",
        windir / "Fonts" / "nyala.ttf",
        Path("/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    pytest.fail("An Ethiopic font is required to build the sample PDF.")


def _write_amharic_pdf(path: Path, pages: list[str], font_path: Path) -> None:
    font = pymupdf.Font(fontfile=str(font_path))
    document = pymupdf.open()
    try:
        for text in pages:
            page = document.new_page()
            writer = pymupdf.TextWriter(page.rect)
            writer.append((72, 96), text, font=font, fontsize=18)
            writer.write_text(page)
        document.save(path)
    finally:
        document.close()


def _write_scanned_amharic_pdf(path: Path, text: str, font_path: Path) -> None:
    font = pymupdf.Font(fontfile=str(font_path))
    text_document = pymupdf.open()
    scanned_document = pymupdf.open()
    try:
        source_page = text_document.new_page()
        writer = pymupdf.TextWriter(source_page.rect)
        writer.append((72, 96), text, font=font, fontsize=18)
        writer.write_text(source_page)
        image = source_page.get_pixmap(dpi=200, alpha=False).tobytes("png")

        scanned_page = scanned_document.new_page()
        scanned_page.insert_image(scanned_page.rect, stream=image)
        scanned_document.save(path)
    finally:
        text_document.close()
        scanned_document.close()


def test_extracts_amharic_pages_and_leaves_pdf_unchanged(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    extracted = tmp_path / "extracted"
    raw.mkdir()
    source = raw / "sample.pdf"
    _write_amharic_pdf(source, [PAGE_ONE, PAGE_TWO], _ethiopic_font())
    original_hash = _sha256(source)

    exit_code = run("sample.pdf", raw, extracted)

    output = extracted / "sample.json"
    assert exit_code == 0
    assert output.is_file()
    assert _sha256(source) == original_hash
    assert not output.read_bytes().startswith(b"\xef\xbb\xbf")

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["filename"] == "sample.pdf"
    assert saved["page_count"] == 2
    assert saved["extraction_method"] == EXTRACTION_METHOD
    assert saved["encoding"] == "utf-8"
    assert [page["page_number"] for page in saved["pages"]] == [1, 2]
    assert [page["extraction_method"] for page in saved["pages"]] == [
        "pymupdf",
        "pymupdf",
    ]
    assert _words(saved["pages"][0]["text"]) == PAGE_ONE
    assert _words(saved["pages"][1]["text"]) == PAGE_TWO
    assert _words(saved["pages"][0]["raw_text"]) == PAGE_ONE
    assert _words(saved["pages"][0]["pymupdf_text"]) == PAGE_ONE
    raw_output = output.read_bytes()
    assert "ቤተ".encode("utf-8") in raw_output
    assert "መጽሐፍ".encode("utf-8") in raw_output
    assert b"\\u1264" not in raw_output


def test_scanned_page_uses_ocr_and_preserves_debug_text(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    extracted = tmp_path / "extracted"
    raw.mkdir()
    source = raw / "scanned.pdf"
    _write_scanned_amharic_pdf(source, PAGE_ONE, _ethiopic_font())
    original_hash = _sha256(source)
    ocr_calls: list[int] = []

    def fake_amharic_ocr(page: pymupdf.Page) -> str:
        ocr_calls.append(page.number + 1)
        return f"  {PAGE_ONE}\u00a0\n"

    document, output = ingest_pdf(
        "scanned.pdf",
        raw,
        extracted,
        ocr_engine=fake_amharic_ocr,
    )

    assert ocr_calls == [1]
    assert _sha256(source) == original_hash
    assert document.extraction_method == "ocr"
    assert document.pages[0].page_number == 1
    assert document.pages[0].extraction_method == "ocr"
    assert document.pages[0].text == PAGE_ONE
    assert document.pages[0].raw_text == f"  {PAGE_ONE}\u00a0\n"
    assert document.pages[0].pymupdf_text == ""
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["pages"][0]["extraction_method"] == "ocr"


def test_quality_check_rejects_legacy_font_gibberish() -> None:
    assert is_text_usable(f"{PAGE_ONE}\nThe Ethiopian Orthodox Church")
    assert not is_text_usable("")
    assert not is_text_usable("h¡ Ai¨H c\u0016¨ `c AHev")


def test_missing_non_pdf_and_escaped_paths_raise(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    extracted = tmp_path / "extracted"
    raw.mkdir()
    (raw / "notes.txt").write_text(PAGE_ONE, encoding="utf-8")

    with pytest.raises(IngestionError, match="not found"):
        ingest_pdf("missing.pdf", raw, extracted)
    with pytest.raises(IngestionError, match="Only .pdf"):
        ingest_pdf("notes.txt", raw, extracted)
    with pytest.raises(IngestionError, match="inside data/raw"):
        ingest_pdf("../outside.pdf", raw, extracted)
    with pytest.raises(IngestionError, match="absolute path"):
        ingest_pdf(str(raw / "notes.txt"), raw, extracted)

    assert list(extracted.glob("*.json")) == []


def test_corrupt_and_encrypted_pdfs_raise(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    extracted = tmp_path / "extracted"
    raw.mkdir()
    corrupt = raw / "corrupt.pdf"
    corrupt.write_bytes(b"%PDF-1.4\nnot a real pdf")

    with pytest.raises(IngestionError, match="Could not open"):
        ingest_pdf("corrupt.pdf", raw, extracted)

    encrypted = raw / "secret.pdf"
    document = pymupdf.open()
    try:
        document.new_page()
        document.save(
            encrypted,
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            owner_pw="owner-secret",
            user_pw="user-secret",
        )
    finally:
        document.close()

    with pytest.raises(IngestionError, match="encrypted"):
        ingest_pdf("secret.pdf", raw, extracted)

    assert run("corrupt.pdf", raw, extracted) == 1
    assert list(extracted.glob("*.json")) == []


def test_app_exposes_ingest_route() -> None:
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in paths
    assert "/ingest" in paths
