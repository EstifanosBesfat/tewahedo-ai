"""Split prepared chunks into focused retrieval units.

The original prepared chunks stay unchanged. Each unit keeps that chunk as
its parent and stays under the embedding token budget, so unrelated windows
do not have to be averaged.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence

from app.preparation.chunker import _is_heading, normalize_whitespace
from app.preparation.schemas import (
    PreparedChunk,
    PreparedDocument,
    RetrievalUnit,
    RetrievalUnitDocument,
)

TokenLength = Callable[[str], int]

E5_TOKEN_LIMIT = 512
E5_TOKEN_MARGIN = 64
DEFAULT_MAX_TOKENS = E5_TOKEN_LIMIT - E5_TOKEN_MARGIN

_SENTENCE_END_RE = re.compile(r"(?:።|፡፡|::|[!?፧፨»”])")
_NUMBERED_TOPIC_RE = re.compile(
    r"^(?:[0-9]+|[፩-፼]+|[ሀለሐመሠረሰሸቀበተቸነኘአከወዐዘየደገጠጨጰጸፀፈፐ])"
    r"[.፦)\-]\s+\S"
)
_SECTION_TITLE_RE = re.compile(
    r"(?:አንደኛው|ሁለተኛው|ሦስተኛው|አራተኛው|አምስተኛው|ስድስተኛው|ሰባተኛው|"
    r"ስምንተኛው|ዘጠነኛው|አሥረኛው|አስረኛው)\s+ትእዛዝ"
    r"|ሰንበትን\s+አክብር"
    r"|ነፍስን\s+መግደል"
    r"|ራስን\s+ማምለክ"
)
_CITATION_RE = re.compile(
    r"(?:[0-9፩-፼]+\s*[፥:.፡]\s*[0-9፩-፼]+)"
)
_EMBEDDED_TOPIC_RE = re.compile(
    r"(?<=[።!?፧፨:፡])\s+(?="
    r"(?:[0-9]+|[፩-፼]+|[ሀለሐመሠረሰሸቀበተቸነኘአከወዐዘየደገጠጨጰጸፀፈፐ])"
    r"[.፦)\-]\s+\S"
    r"|(?:አንደኛው|ሁለተኛው|ሦስተኛው|አራተኛው|አምስተኛው|ስድስተኛው|ሰባተኛው|"
    r"ስምንተኛው|ዘጠነኛው|አሥረኛው|አስረኛው)\s+ትእዛዝ"
    r"|ሰንበትን\s+አክብር"
    r"|ነፍስን\s+መግደል"
    r"|ራስን\s+ማምለክ"
    r")"
)


def parent_chunk_id(retrieval_chunk_id: str) -> str:
    """Return the prepared-chunk id stored in a retrieval-unit id."""

    marker = ":unit-"
    if marker not in retrieval_chunk_id:
        return retrieval_chunk_id
    return retrieval_chunk_id.split(marker, 1)[0]


def _split_embedded_topics(paragraph: str) -> list[str]:
    pieces: list[str] = []
    start = 0
    for match in _EMBEDDED_TOPIC_RE.finditer(paragraph):
        following = paragraph[match.end() :]
        if not _starts_new_section(following):
            continue
        piece = paragraph[start : match.start()].strip()
        if piece:
            pieces.append(piece)
        start = match.end()
    tail = paragraph[start:].strip()
    if tail:
        pieces.append(tail)
    return pieces or [paragraph.strip()]


def _paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    for part in text.split("\n\n"):
        cleaned = part.strip()
        if not cleaned:
            continue
        paragraphs.extend(_split_embedded_topics(cleaned))
    return paragraphs


def _looks_like_citation(text: str) -> bool:
    words = text.split()
    return bool(
        _CITATION_RE.search(text) and len(text) <= 48 and len(words) <= 8
    )


def _is_numbered_topic(paragraph: str) -> bool:
    match = _NUMBERED_TOPIC_RE.match(paragraph.strip())
    if match is None:
        return False
    payload = paragraph.strip()[match.end() :].strip()
    return not _looks_like_citation(payload)


def _starts_new_section(paragraph: str) -> bool:
    text = paragraph.strip()
    if _looks_like_citation(text):
        return False
    if _is_heading(text) or _is_numbered_topic(text):
        return True
    title = _SECTION_TITLE_RE.search(text)
    if title is None:
        return False
    return len(text[: title.start()].split()) <= 3


def _sections(paragraphs: Sequence[str]) -> list[list[str]]:
    sections: list[list[str]] = []
    current: list[str] = []
    for paragraph in paragraphs:
        if current and _starts_new_section(paragraph):
            sections.append(current)
            current = [paragraph]
        else:
            current.append(paragraph)
    if current:
        sections.append(current)
    return sections


def _is_citation_fragment(sentence: str) -> bool:
    words = sentence.split()
    return (
        len(sentence) <= 48
        and len(words) <= 8
        and _CITATION_RE.search(sentence) is not None
    )


def _sentences(paragraph: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    for match in _SENTENCE_END_RE.finditer(paragraph):
        sentence = paragraph[start : match.end()].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    remainder = paragraph[start:].strip()
    if remainder:
        sentences.append(remainder)
    if not sentences:
        return [paragraph.strip()]

    glued: list[str] = []
    for sentence in sentences:
        if glued and _is_citation_fragment(sentence):
            glued[-1] = f"{glued[-1]} {sentence}"
        else:
            glued.append(sentence)
    return glued


def _reference_atoms(text: str) -> list[str]:
    """Keep a biblical citation attached to the word before it."""

    atoms: list[str] = []
    for word in text.split():
        if atoms and _CITATION_RE.search(word) and not _CITATION_RE.search(atoms[-1]):
            atoms[-1] = f"{atoms[-1]} {word}"
        else:
            atoms.append(word)
    return atoms


def _fit_atoms(
    atoms: Sequence[str],
    token_length: TokenLength,
    max_tokens: int,
    prefix: str = "",
) -> tuple[list[str], list[str]]:
    chosen: list[str] = []
    for index, atom in enumerate(atoms):
        body = " ".join([*chosen, atom])
        candidate = f"{prefix}\n\n{body}" if prefix else body
        if token_length(candidate) > max_tokens:
            if not chosen:
                return [], list(atoms)
            return chosen, list(atoms[index:])
        chosen.append(atom)
    return chosen, []


def _split_oversized_piece(
    text: str,
    token_length: TokenLength,
    max_tokens: int,
) -> list[str]:
    atoms = _reference_atoms(text)
    if len(atoms) <= 1:
        return [text]
    pieces: list[str] = []
    remaining = atoms
    while remaining:
        chosen, remaining = _fit_atoms(remaining, token_length, max_tokens)
        if not chosen:
            pieces.append(remaining[0])
            remaining = remaining[1:]
            continue
        pieces.append(" ".join(chosen))
    return pieces


def _pieces_within_limit(
    paragraph: str,
    token_length: TokenLength,
    max_tokens: int,
) -> list[str]:
    if token_length(paragraph) <= max_tokens:
        return [paragraph]
    pieces: list[str] = []
    current: list[str] = []
    for sentence in _sentences(paragraph):
        if token_length(sentence) > max_tokens:
            if current:
                pieces.append(" ".join(current))
                current = []
            pieces.extend(
                _split_oversized_piece(sentence, token_length, max_tokens)
            )
            continue
        candidate = " ".join([*current, sentence])
        if current and token_length(candidate) > max_tokens:
            pieces.append(" ".join(current))
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        pieces.append(" ".join(current))
    return pieces


def _bind_opening_heading(
    pieces: list[str],
    token_length: TokenLength,
    max_tokens: int,
) -> list[str]:
    if len(pieces) < 2 or not _is_heading(pieces[0]):
        return pieces
    chosen, remainder = _fit_atoms(
        _reference_atoms(pieces[1]),
        token_length,
        max_tokens,
        prefix=pieces[0],
    )
    if not chosen:
        return pieces
    bound = f"{pieces[0]}\n\n{' '.join(chosen)}"
    rest = " ".join(remainder)
    following = _pieces_within_limit(rest, token_length, max_tokens) if rest else []
    return [bound, *following, *pieces[2:]]


def _pack_section(
    paragraphs: Sequence[str],
    token_length: TokenLength,
    max_tokens: int,
) -> list[str]:
    pieces = _bind_opening_heading(
        [
            piece
            for paragraph in paragraphs
            for piece in _pieces_within_limit(paragraph, token_length, max_tokens)
        ],
        token_length,
        max_tokens,
    )
    packed: list[str] = []
    current: list[str] = []
    for piece in pieces:
        candidate = "\n\n".join([*current, piece])
        if current and token_length(candidate) > max_tokens:
            packed.append("\n\n".join(current))
            current = [piece]
        else:
            current.append(piece)
    if current:
        packed.append("\n\n".join(current))
    return packed


def _pages_for_text(
    text: str,
    page_text: Mapping[int, str],
    parent: PreparedChunk,
) -> tuple[int, int]:
    if not page_text:
        return parent.page_start, parent.page_end
    found: list[int] = []
    for paragraph in _paragraphs(text):
        needle = normalize_whitespace(paragraph)[:80]
        matches = [
            page_number
            for page_number, page in page_text.items()
            if needle and needle in normalize_whitespace(page)
        ]
        if matches:
            found.append(min(matches))
    if not found:
        return parent.page_start, parent.page_end
    return min(found), max(found)


def refine_prepared_document(
    document: PreparedDocument,
    token_length: TokenLength,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    page_text: Mapping[int, str] | None = None,
) -> RetrievalUnitDocument:
    """Derive retrieval units without modifying the prepared document."""

    if max_tokens < 1:
        raise ValueError("max_tokens must be at least 1")
    pages = page_text or {}
    units: list[RetrievalUnit] = []
    for chunk in document.chunks:
        parent_pages = {
            page_number: text
            for page_number, text in pages.items()
            if chunk.page_start <= page_number <= chunk.page_end
        }
        section_texts = [
            packed
            for section in _sections(_paragraphs(chunk.text))
            for packed in _pack_section(section, token_length, max_tokens)
        ]
        for index, text in enumerate(section_texts, start=1):
            length = token_length(text)
            if length > max_tokens:
                raise ValueError(
                    f"{chunk.chunk_id} unit {index} uses {length} tokens; "
                    f"limit is {max_tokens}"
                )
            page_start, page_end = _pages_for_text(text, parent_pages, chunk)
            units.append(
                RetrievalUnit(
                    chunk_id=f"{chunk.chunk_id}:unit-{index:02d}",
                    document_id=chunk.document_id,
                    page_start=page_start,
                    page_end=page_end,
                    text=text,
                    extraction_method=chunk.extraction_method,
                    source_quality_score=chunk.source_quality_score,
                    parent_chunk_id=chunk.chunk_id,
                    parent_page_start=chunk.page_start,
                    parent_page_end=chunk.page_end,
                    token_length=length,
                )
            )
    return RetrievalUnitDocument(
        document_id=document.document_id,
        source_filename=document.source_filename,
        parent_chunk_count=len(document.chunks),
        max_tokens=max_tokens,
        unit_count=len(units),
        units=units,
    )
