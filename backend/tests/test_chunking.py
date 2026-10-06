"""Tests for post-extraction paragraph reconstruction and chunking."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from app.preparation.chunker import (
    SourceBlock,
    chunk_blocks,
    normalize_whitespace,
    prepare_document,
    reconstruct_page_paragraphs,
)
from app.preparation.schemas import ChunkingConfig, PreparedDocument
from scripts.prepare_chunks import run


def _page(
    page_number: int,
    text: str,
    score: float = 90.0,
    method: str = "ocr",
) -> dict:
    return {
        "page_number": page_number,
        "text": text,
        "extraction_method": method,
        "raw_text": f"raw page {page_number}",
        "quality": {"score": score},
    }


def _document(pages: list[dict]) -> dict:
    return {
        "filename": "sample.pdf",
        "page_count": len(pages),
        "extraction_method": "mixed",
        "encoding": "utf-8",
        "pages": pages,
    }


def test_reconstructs_wrapped_lines_without_losing_source_text() -> None:
    page = _page(
        3,
        "ሦስተኛው ትእዛዝ\n"
        "ይህ የአንድ ረጅም አንቀጽ የመጀመሪያ መስመር\n"
        "ሲሆን ይህ ደግሞ ቀጣዩ መስመር ነው።\n"
        "ዘጸ. 20፥7",
    )

    blocks = reconstruct_page_paragraphs(page)

    assert blocks[0].kind == "heading"
    assert blocks[0].text == "ሦስተኛው ትእዛዝ"
    assert "መስመር ሲሆን" in blocks[1].text
    assert blocks[1].text.endswith("ዘጸ. 20፥7")
    assert all(block.page_number == 3 for block in blocks)
    reconstructed = normalize_whitespace(" ".join(block.text for block in blocks))
    assert reconstructed == normalize_whitespace(page["text"])


def test_heading_keyword_inside_body_text_does_not_split_the_paragraph() -> None:
    page = _page(
        5,
        "ይህ ትእዛዝ ለሁሉም ሰው የተሰጠ ነው፡፡ ቀጣዩ ክፍል\n"
        "የዚሁን አሳብ ማብራሪያ ይቀጥላል።\n"
        "መደምደሚያ አበጅተውለት የራሳቸውን ሐሳብ እንዲ\n"
        "ጨምሩ አይገባም።",
    )

    blocks = reconstruct_page_paragraphs(page)

    assert len(blocks) == 2
    assert all(block.kind == "paragraph" for block in blocks)
    assert "ቀጣዩ ክፍል የዚሁን" in blocks[0].text
    assert "ሐሳብ እንዲ ጨምሩ" in blocks[1].text


def test_prepare_document_does_not_mutate_extracted_pages_or_raw_text() -> None:
    extracted = _document(
        [
            _page(1, "መግቢያ\nይህ የመጀመሪያው ገጽ ጽሑፍ ነው።"),
            _page(2, "ይህ የሁለተኛው ገጽ ጽሑፍ ነው።", score=75.0),
        ]
    )
    original = copy.deepcopy(extracted)

    prepared = prepare_document(
        extracted,
        ChunkingConfig(target_chars=500, overlap_chars=40),
    )

    assert extracted == original
    assert extracted["pages"][0]["raw_text"] == "raw page 1"
    assert extracted["pages"][1]["text"] == "ይህ የሁለተኛው ገጽ ጽሑፍ ነው።"
    assert prepared.source_page_count == 2


def test_chunk_schema_page_range_method_and_conservative_quality() -> None:
    extracted = _document(
        [
            _page(1, "የመጀመሪያው ገጽ ጽሑፍ ነው።", score=91.0),
            _page(
                2,
                "የሁለተኛው ገጽ ጽሑፍ ነው።",
                score=72.5,
                method="pymupdf",
            ),
        ]
    )

    prepared = prepare_document(
        extracted,
        ChunkingConfig(target_chars=500, overlap_chars=40),
    )

    assert len(prepared.chunks) == 1
    chunk = prepared.chunks[0]
    assert chunk.chunk_id == "sample:chunk-0001"
    assert chunk.document_id == "sample"
    assert (chunk.page_start, chunk.page_end) == (1, 2)
    assert chunk.extraction_method == "mixed"
    assert chunk.source_quality_score == 72.5
    assert set(chunk.model_dump()) == {
        "chunk_id",
        "document_id",
        "page_start",
        "page_end",
        "text",
        "extraction_method",
        "source_quality_score",
    }


def test_chunk_overlap_is_configurable_and_bounded() -> None:
    first = " ".join(["መጀመሪያ"] * 22) + "።"
    second = " ".join(["ሁለተኛ"] * 22) + "።"
    blocks = [
        SourceBlock(first, 1, "ocr", 88.0),
        SourceBlock(second, 1, "ocr", 88.0),
    ]

    chunks = chunk_blocks(
        blocks,
        "sample",
        ChunkingConfig(target_chars=200, overlap_chars=35),
    )

    assert len(chunks) == 2
    overlap = chunks[1].text.split("\n\n", maxsplit=1)[0]
    assert overlap in chunks[0].text
    assert len(overlap) <= 35
    assert len(chunks[1].text) <= 200


def test_oversized_sentence_does_not_strand_a_tiny_prefix_chunk() -> None:
    text = "አጭር መግቢያ። " + " ".join(["ረጅም"] * 80)
    blocks = [SourceBlock(text, 4, "ocr", 84.0)]

    chunks = chunk_blocks(
        blocks,
        "sample",
        ChunkingConfig(target_chars=200, overlap_chars=0),
    )

    assert len(chunks) >= 2
    assert len(chunks[0].text) >= 150
    assert all(len(chunk.text) <= 200 for chunk in chunks)
    assert normalize_whitespace(" ".join(chunk.text for chunk in chunks)) == text


def test_script_writes_processed_json_without_changing_input(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "extracted"
    output_dir = tmp_path / "processed"
    source_dir.mkdir()
    input_path = source_dir / "sample.json"
    extracted = _document(
        [
            _page(1, "መግቢያ\nየመጀመሪያው ገጽ ጽሑፍ ነው።"),
            _page(2, "የሁለተኛው ገጽ ጽሑፍ ነው።", score=81.0),
        ]
    )
    original_bytes = (
        json.dumps(extracted, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    input_path.write_bytes(original_bytes)

    result = run(
        "sample.pdf",
        target_chars=300,
        overlap_chars=30,
        source_dir=source_dir,
        output_dir=output_dir,
    )

    assert result == 0
    assert input_path.read_bytes() == original_bytes
    output = PreparedDocument.model_validate_json(
        (output_dir / "sample.chunks.json").read_text(encoding="utf-8")
    )
    assert output.document_id == "sample"
    assert output.source_page_count == 2
    assert {chunk.page_start for chunk in output.chunks}.issubset({1, 2})
    assert {chunk.page_end for chunk in output.chunks}.issubset({1, 2})
