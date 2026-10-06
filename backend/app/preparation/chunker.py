"""Deterministic paragraph reconstruction and semantic text chunking."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from app.preparation.schemas import (
    ChunkingConfig,
    PreparedChunk,
    PreparedDocument,
)

_SPACE_RE = re.compile(r"\s+")
_HEADING_PREFIX_RE = re.compile(
    r"^(?:[0-9፩-፼]+|[ሀለሐመሠረሰሸቀበተቸነኘአከወዐዘየደገጠጨጰጸፀፈፐ])"
    r"(?:[\s.)፡፦:-]+)"
)
_TERMINAL_RE = re.compile(r"(?:።|፡፡|::|[.!?፧፨»”])\s*$")
_SENTENCE_END_RE = re.compile(r"(?:።|፡፡|::|[!?፧፨»”])")
_BIBLICAL_REFERENCE_RE = re.compile(
    r"(?:[0-9፩-፼]+\s*[፥:]\s*[0-9፩-፼]+)"
)


@dataclass(frozen=True)
class SourceBlock:
    """A reconstructed source span that still carries page provenance."""

    text: str
    page_number: int
    extraction_method: str
    quality_score: float
    kind: str = "paragraph"


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace only; useful for proving source preservation."""

    return _SPACE_RE.sub(" ", text).strip()


def _is_heading(line: str) -> bool:
    normalized = normalize_whitespace(line)
    if not normalized or len(normalized) > 100 or _TERMINAL_RE.search(normalized):
        return False
    words = normalized.split()
    word_count = len(words)
    if word_count > 14:
        return False
    has_heading_prefix = bool(_HEADING_PREFIX_RE.match(normalized))
    starts_named_section = (
        words[0] in {"መግቢያ", "ማውጫ", "መደምደሚያ"}
        and word_count <= 3
    ) or (
        words[0] in {"ምዕራፍ", "ክፍል"}
        and word_count <= 5
    )
    names_command = any(
        word.startswith(("ትእዛዝ", "ትዕዛዝ"))
        for word in words[:3]
    )
    has_short_heading_keyword = bool(
        word_count <= 10
        and (starts_named_section or names_command)
        and not _SENTENCE_END_RE.search(normalized)
    )
    return has_heading_prefix or has_short_heading_keyword


def reconstruct_page_paragraphs(page: dict[str, Any]) -> list[SourceBlock]:
    """Join visual OCR line wraps while retaining meaningful text boundaries."""

    page_number = int(page["page_number"])
    extraction_method = str(page["extraction_method"])
    quality_score = float(page["quality"]["score"])
    lines = [
        normalize_whitespace(line)
        for line in str(page.get("text", "")).splitlines()
        if normalize_whitespace(line)
    ]

    blocks: list[SourceBlock] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        blocks.append(
            SourceBlock(
                text=" ".join(paragraph_lines),
                page_number=page_number,
                extraction_method=extraction_method,
                quality_score=quality_score,
            )
        )
        paragraph_lines.clear()

    for line in lines:
        if _is_heading(line):
            flush_paragraph()
            blocks.append(
                SourceBlock(
                    text=line,
                    page_number=page_number,
                    extraction_method=extraction_method,
                    quality_score=quality_score,
                    kind="heading",
                )
            )
            continue

        if (
            len(line) <= 100
            and _BIBLICAL_REFERENCE_RE.search(line)
            and not paragraph_lines
            and blocks
            and blocks[-1].kind == "paragraph"
        ):
            blocks[-1] = replace(
                blocks[-1],
                text=f"{blocks[-1].text} {line}",
            )
            continue

        paragraph_lines.append(line)
        if _TERMINAL_RE.search(line):
            flush_paragraph()

    flush_paragraph()
    return blocks


def reconstruct_document_paragraphs(
    pages: Iterable[dict[str, Any]],
) -> list[SourceBlock]:
    """Reconstruct each page independently so page boundaries cannot be lost."""

    blocks: list[SourceBlock] = []
    previous_page = 0
    for page in pages:
        page_number = int(page["page_number"])
        if page_number <= previous_page:
            raise ValueError("pages must have unique, increasing page numbers")
        blocks.extend(reconstruct_page_paragraphs(page))
        previous_page = page_number
    return blocks


def _split_by_words(block: SourceBlock, limit: int) -> list[SourceBlock]:
    words = block.text.split()
    pieces: list[SourceBlock] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and len(candidate) > limit:
            pieces.append(replace(block, text=" ".join(current)))
            current = [word]
        else:
            current.append(word)
    if current:
        pieces.append(replace(block, text=" ".join(current)))
    return pieces


def _split_long_block(block: SourceBlock, limit: int) -> list[SourceBlock]:
    if len(block.text) <= limit:
        return [block]

    sentences: list[str] = []
    start = 0
    for match in _SENTENCE_END_RE.finditer(block.text):
        sentence = block.text[start : match.end()].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    remainder = block.text[start:].strip()
    if remainder:
        sentences.append(remainder)

    if len(sentences) <= 1 or any(
        len(sentence) > limit for sentence in sentences
    ):
        return _split_by_words(block, limit)

    pieces: list[SourceBlock] = []
    current: list[str] = []
    for sentence in sentences:
        candidate = " ".join([*current, sentence])
        if current and len(candidate) > limit:
            pieces.append(replace(block, text=" ".join(current)))
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        pieces.append(replace(block, text=" ".join(current)))
    return pieces


def _render_blocks(blocks: list[SourceBlock]) -> str:
    return "\n\n".join(block.text for block in blocks if block.text).strip()


def _overlap_tail(
    blocks: list[SourceBlock],
    overlap_chars: int,
) -> list[SourceBlock]:
    if overlap_chars <= 0 or not blocks:
        return []

    selected: list[SourceBlock] = []
    used = 0
    for block in reversed(blocks):
        separator = 2 if selected else 0
        if used + separator + len(block.text) <= overlap_chars:
            selected.append(block)
            used += separator + len(block.text)
            continue
        if selected:
            break

        start = max(0, len(block.text) - overlap_chars)
        if start:
            next_space = block.text.find(" ", start)
            if next_space != -1:
                start = next_space + 1
        suffix = block.text[start:].strip()
        if suffix:
            selected.append(replace(block, text=suffix, kind="overlap"))
        break
    return list(reversed(selected))


def _chunk_metadata(blocks: list[SourceBlock]) -> tuple[int, int, str, float]:
    pages = [block.page_number for block in blocks]
    methods = {block.extraction_method for block in blocks}
    method = next(iter(methods)) if len(methods) == 1 else "mixed"
    quality = min(block.quality_score for block in blocks)
    return min(pages), max(pages), method, quality


def chunk_blocks(
    blocks: list[SourceBlock],
    document_id: str,
    config: ChunkingConfig,
) -> list[PreparedChunk]:
    """Pack source blocks around the target size with bounded text overlap."""

    units = [
        unit
        for block in blocks
        for unit in _split_long_block(block, config.target_chars)
    ]
    grouped: list[list[SourceBlock]] = []
    current: list[SourceBlock] = []

    def emit() -> list[SourceBlock]:
        if not current:
            return []
        grouped.append(list(current))
        return _overlap_tail(current, config.overlap_chars)

    for unit in units:
        if current:
            page_changed = current[-1].page_number != unit.page_number
            sufficiently_full = len(_render_blocks(current)) >= int(
                config.target_chars * 0.65
            )
            if unit.kind == "heading" or (page_changed and sufficiently_full):
                emit()
                current = []

        candidate = [*current, unit]
        if current and len(_render_blocks(candidate)) > config.target_chars:
            overlap = emit()
            while overlap and len(_render_blocks([*overlap, unit])) > config.target_chars:
                overlap.pop(0)
            current = overlap
        current.append(unit)

    if current:
        grouped.append(current)

    chunks: list[PreparedChunk] = []
    for index, chunk_blocks_value in enumerate(grouped, start=1):
        page_start, page_end, method, quality = _chunk_metadata(chunk_blocks_value)
        chunks.append(
            PreparedChunk(
                chunk_id=f"{document_id}:chunk-{index:04d}",
                document_id=document_id,
                page_start=page_start,
                page_end=page_end,
                text=_render_blocks(chunk_blocks_value),
                extraction_method=method,
                source_quality_score=quality,
            )
        )
    return chunks


def prepare_document(
    extracted: dict[str, Any],
    config: ChunkingConfig | None = None,
) -> PreparedDocument:
    """Prepare chunks from an extracted JSON object without mutating it."""

    selected_config = config or ChunkingConfig()
    source_filename = str(extracted["filename"])
    document_id = Path(source_filename).stem
    pages = extracted["pages"]
    blocks = reconstruct_document_paragraphs(pages)
    chunks = chunk_blocks(blocks, document_id, selected_config)
    return PreparedDocument(
        document_id=document_id,
        source_filename=source_filename,
        source_page_count=int(extracted["page_count"]),
        chunking=selected_config,
        chunk_count=len(chunks),
        chunks=chunks,
    )


def load_and_prepare(
    input_path: Path,
    config: ChunkingConfig | None = None,
) -> PreparedDocument:
    """Read extracted UTF-8 JSON and prepare it without writing to the source."""

    with input_path.open("r", encoding="utf-8") as source:
        extracted = json.load(source)
    return prepare_document(extracted, config)
