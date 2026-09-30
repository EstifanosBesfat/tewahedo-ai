"""Tests for text-based PDF ingestion."""

import hashlib
import json
import os
from pathlib import Path

import fitz
import pytest

from app.ingestion.extractor import EXTRACTION_METHOD, IngestionError, ingest_pdf
from app.main import app
from scripts.extract_pdf import run

PAGE_ONE = "ቤተ ክርስቲያን"
PAGE_TWO = "መጽሐፍ ቅዱስ"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


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
    font = fitz.Font(fontfile=str(font_path))
    document = fitz.open()
    try:
        for text in pages:
            page = document.new_page()
            writer = fitz.TextWriter(page.rect)
            writer.append((72, 96), text, font=font, fontsize=18)
            writer.write_text(page)
        document.save(path)
    finally:
        document.close()


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
    assert PAGE_ONE in saved["pages"][0]["text"]
    assert PAGE_TWO in saved["pages"][1]["text"]
    assert PAGE_TWO not in saved["pages"][0]["text"]
    assert PAGE_ONE.encode("utf-8") in output.read_bytes()


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
    document = fitz.open()
    try:
        document.new_page()
        document.save(
            encrypted,
            encryption=fitz.PDF_ENCRYPT_AES_256,
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
