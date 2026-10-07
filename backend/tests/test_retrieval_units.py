"""Tests for focused retrieval units derived from prepared chunks."""

from __future__ import annotations

from app.preparation.retrieval_units import (
    parent_chunk_id,
    refine_prepared_document,
)
from app.preparation.schemas import (
    ChunkingConfig,
    PreparedChunk,
    PreparedDocument,
)


def _chunk(chunk_id: str, text: str, page_start: int = 2, page_end: int = 3) -> PreparedChunk:
    return PreparedChunk(
        chunk_id=chunk_id,
        document_id="sample",
        page_start=page_start,
        page_end=page_end,
        text=text,
        extraction_method="ocr",
        source_quality_score=80.0,
    )


def _document(chunks: list[PreparedChunk]) -> PreparedDocument:
    return PreparedDocument(
        document_id="sample",
        source_filename="sample.pdf",
        source_page_count=3,
        chunking=ChunkingConfig(),
        chunk_count=len(chunks),
        chunks=chunks,
    )


def _tokens(text: str) -> int:
    return len(text.split())


def test_numbered_topics_and_sabbath_title_stay_apart() -> None:
    tablets = "\n\n".join(
        [
            "መ. ሁለቴ ጽላት",
            "አሠርቱ ትእዛዛት ሁለት ክፍሎች አሏቸው።",
            "የመጀመሪያው ጽላት ስለ እግዚአብሔር ነው።",
            "፲. መግደል ከሙሴ በፊትም ኃጢአት ነበር።",
        ]
    )
    sabbath = "\n\n".join(
        [
            "ስሙን በከንቱ የሚጠሩ ይመደባሉ።",
            "የተከበረ ስም አጠራር ከምግባር ጋር መገኘት አለበት።",
            "ሥዕል ሰንበትን አክብር የሰንበትን ቀን ትቀድሰው።",
        ]
    )
    source = _document(
        [
            _chunk("sample:chunk-0005", tablets),
            _chunk("sample:chunk-0031", sabbath, page_start=11, page_end=11),
        ]
    )
    before = source.model_dump_json()

    refined = refine_prepared_document(source, _tokens, max_tokens=12)

    assert source.model_dump_json() == before
    by_parent: dict[str, list[str]] = {}
    for unit in refined.units:
        by_parent.setdefault(unit.parent_chunk_id, []).append(unit.text)
        assert unit.token_length <= 12
        assert parent_chunk_id(unit.chunk_id) == unit.parent_chunk_id
        assert unit.extraction_method == "ocr"
        assert unit.source_quality_score == 80.0

    tablet_units = by_parent["sample:chunk-0005"]
    assert any("ሁለቴ ጽላት" in text and "መግደል" not in text for text in tablet_units)
    assert any(text.startswith("፲. መግደል") for text in tablet_units)
    sabbath_units = by_parent["sample:chunk-0031"]
    assert any("ስሙን በከንቱ" in text and "ሰንበትን" not in text for text in sabbath_units)
    assert any("ሰንበትን አክብር" in text and "ስሙን በከንቱ" not in text for text in sabbath_units)


def test_numbered_topic_inside_a_paragraph_starts_its_own_unit() -> None:
    mixed = (
        "2. ዝሙት ከሙሴ በፊትም ኃጢአት ነበር። ዘፍ. 39፥9። "
        "ያረጋግጣሉ: 5. መስረቅም ከሙሴ በፊት ኃጢአት ነበር።"
    )
    refined = refine_prepared_document(
        _document([_chunk("sample:chunk-0006", mixed, page_start=3, page_end=3)]),
        _tokens,
        max_tokens=40,
    )

    assert len(refined.units) == 2
    assert "ዝሙት" in refined.units[0].text
    assert "39፥9" in refined.units[0].text
    assert refined.units[1].text.startswith("5. መስረቅ")
    assert "ዝሙት" not in refined.units[1].text


def test_citation_number_does_not_become_its_own_topic() -> None:
    body = "ወላጆችን መርዳት የክብር ገጽታ ነው። ምሳ 10፡ ፲- 23:24።"
    refined = refine_prepared_document(
        _document([_chunk("sample:chunk-0043", body, page_start=14, page_end=14)]),
        _tokens,
        max_tokens=40,
    )

    assert len(refined.units) == 1
    assert "23:24" in refined.units[0].text
    assert "ወላጆችን" in refined.units[0].text


def test_citation_stays_with_its_sentence_and_units_fit() -> None:
    body = " ".join(["ረጅም"] * 20) + "። ዘጸ 20፥13። " + " ".join(["ሌላ"] * 8) + "።"
    refined = refine_prepared_document(
        _document([_chunk("sample:chunk-0009", body, page_start=4, page_end=4)]),
        _tokens,
        max_tokens=12,
        page_text={4: body},
    )

    assert refined.unit_count >= 2
    assert all(unit.token_length <= 12 for unit in refined.units)
    assert all(unit.page_start == 4 and unit.page_end == 4 for unit in refined.units)
    assert any("ዘጸ 20፥13" in unit.text for unit in refined.units)
    citation_unit = next(unit for unit in refined.units if "ዘጸ" in unit.text)
    assert "ረጅም" in citation_unit.text
    assert not citation_unit.text.startswith("ዘጸ")
