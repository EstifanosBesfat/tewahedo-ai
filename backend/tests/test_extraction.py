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
from app.ingestion.ocr import OcrLine, OcrResult, render_page
from app.ingestion.processing import (
    assess_quality,
    clean_ocr_result,
    detect_repeated_margin_lines,
)
from app.ingestion.similarity import body_text_similarity, compare_documents
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


def test_structured_ocr_cleans_noise_and_preserves_raw_text(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    extracted = tmp_path / "extracted"
    raw.mkdir()
    source = raw / "scanned.pdf"
    _write_scanned_amharic_pdf(source, PAGE_ONE, _ethiopic_font())

    lines = (
        OcrLine("ተደጋጋሚ ርዕስ", 95, 20, 20, 500, 50),
        OcrLine("www.ethiopianorthodox.org", 90, 20, 70, 600, 95),
        OcrLine("ይህ ትምህርት በጣም ABC ቅዱ", 88, 20, 300, 900, 330),
        OcrLine("ስን መጽሐፍ", 92, 10, 340, 500, 370),
    )
    result = OcrResult(
        raw_text="\n".join(line.text for line in lines) + "\n",
        lines=lines,
        language="amh",
        dpi=300,
        psm=3,
        preprocessing="grayscale_autocontrast",
        image_width=1000,
        image_height=1000,
        mean_confidence=91.25,
    )

    document, _ = ingest_pdf(
        "scanned.pdf",
        raw,
        extracted,
        ocr_engine=lambda _page: result,
    )

    page = document.pages[0]
    assert page.raw_text == result.raw_text
    assert "www.ethiopianorthodox.org" not in page.text
    assert "ABC" not in page.text
    assert "ቅዱስን መጽሐፍ" in page.text.replace("\n", " ")
    assert page.repaired_line_wraps == 1
    assert page.ocr is not None
    assert page.ocr.language == "amh"
    assert page.quality.mean_confidence == 91.25
    assert "sparse_text" in page.quality.flags
    assert "ABC" in page.removed_fragments


def test_render_page_is_grayscale_and_quality_flags_sparse_text(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.pdf"
    _write_amharic_pdf(source, [PAGE_ONE], _ethiopic_font())
    with pymupdf.open(source) as document:
        image = render_page(document[0])
        try:
            assert image.mode == "L"
        finally:
            image.close()

    quality = assess_quality("ABC", 40.0, 0)
    assert quality.score < 75
    assert "sparse_text" in quality.flags
    assert "low_ocr_confidence" in quality.flags
    assert "review_recommended" in quality.flags


def test_repeated_margin_layout_removes_header_and_footer() -> None:
    lines = (
        OcrLine("header one", 90, 10, 20, 500, 45),
        OcrLine("header two", 90, 10, 55, 500, 80),
        OcrLine(PAGE_ONE, 90, 10, 250, 800, 280),
        OcrLine("garbled footer", 70, 10, 920, 500, 950),
    )
    result = OcrResult(
        raw_text="\n".join(line.text for line in lines),
        lines=lines,
        language="amh",
        dpi=300,
        psm=3,
        preprocessing="grayscale_autocontrast",
        image_width=1000,
        image_height=1000,
        mean_confidence=85,
    )
    patterns = detect_repeated_margin_lines([result, result])
    cleaned = clean_ocr_result(result, patterns)

    assert cleaned.text == PAGE_ONE
    assert len(cleaned.removed_fragments) == 3


def test_document_similarity_uses_body_content_and_rendered_pages(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    font = _ethiopic_font()
    _write_amharic_pdf(first, [PAGE_ONE], font)
    _write_amharic_pdf(second, [PAGE_TWO], font)

    exact = compare_documents(first, first, PAGE_ONE, PAGE_ONE)
    distinct = compare_documents(first, second, PAGE_ONE, PAGE_TWO)

    assert exact.duplicate
    assert exact.same_pdf_bytes
    assert not distinct.duplicate
    assert body_text_similarity(
        f"www.ethiopianorthodox.org\n{PAGE_ONE}",
        PAGE_ONE,
    ) == 1.0
