"""Conservative OCR cleanup and deterministic page-quality assessment."""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.ingestion.ocr import OcrLine, OcrResult

ETHIOPIC_START = 0x1200
ETHIOPIC_END = 0x139F
URL_MARKER = "ethiopianorthodox"
LATIN_ARTIFACT = re.compile(r"(?<![A-Za-z])[A-Za-z]{1,4}(?![A-Za-z])")
TOP_BAND_PATTERN = "__repeated_top_band__"
BOTTOM_BAND_PATTERN = "__repeated_bottom_band__"


@dataclass(frozen=True)
class CleanedPage:
    text: str
    removed_fragments: tuple[str, ...]
    repaired_line_wraps: int


@dataclass(frozen=True)
class QualityAssessment:
    score: float
    mean_confidence: float | None
    visible_characters: int
    ethiopic_ratio: float
    latin_ratio: float
    suspicious_characters: int
    removed_fragment_count: int
    flags: tuple[str, ...]


def _is_ethiopic(character: str) -> bool:
    return ETHIOPIC_START <= ord(character) <= ETHIOPIC_END


def _canonical_line(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _is_margin(line: OcrLine, result: OcrResult) -> bool:
    return line.top <= result.image_height * 0.16 or line.bottom >= (
        result.image_height * 0.90
    )


def _is_url(text: str) -> bool:
    compact = _canonical_line(text)
    return URL_MARKER in compact or (
        "ethiopian" in compact and "orthodox" in compact
    )


def detect_repeated_margin_lines(results: list[OcrResult]) -> tuple[str, ...]:
    """Find fuzzy-equivalent lines repeated in document margins."""
    if len(results) < 2:
        return ()

    clusters: list[dict[str, object]] = []
    for page_index, result in enumerate(results):
        for line in result.lines:
            if not _is_margin(line, result):
                continue
            canonical = _canonical_line(line.text)
            if len(canonical) < 6:
                continue
            match = None
            for cluster in clusters:
                representative = str(cluster["representative"])
                if SequenceMatcher(None, canonical, representative).ratio() >= 0.72:
                    match = cluster
                    break
            if match is None:
                clusters.append(
                    {"representative": canonical, "pages": {page_index}}
                )
            else:
                pages = match["pages"]
                if isinstance(pages, set):
                    pages.add(page_index)

    minimum_pages = max(2, math.ceil(len(results) * 0.50))
    patterns = [
        str(cluster["representative"])
        for cluster in clusters
        if isinstance(cluster["pages"], set)
        and len(cluster["pages"]) >= minimum_pages
    ]
    repeated_top_layout = sum(
        sum(line.bottom <= result.image_height * 0.11 for line in result.lines)
        >= 2
        for result in results
    )
    repeated_bottom_layout = sum(
        any(line.top >= result.image_height * 0.90 for line in result.lines)
        for result in results
    )
    if repeated_top_layout >= minimum_pages:
        patterns.append(TOP_BAND_PATTERN)
    if repeated_bottom_layout >= minimum_pages:
        patterns.append(BOTTOM_BAND_PATTERN)
    return tuple(patterns)


def _matches_repeated_margin(
    line: OcrLine,
    result: OcrResult,
    patterns: tuple[str, ...],
) -> bool:
    if not _is_margin(line, result):
        return False
    if (
        TOP_BAND_PATTERN in patterns
        and line.bottom <= result.image_height * 0.11
    ):
        return True
    if (
        BOTTOM_BAND_PATTERN in patterns
        and line.top >= result.image_height * 0.90
        and (line.right - line.left) <= result.image_width * 0.65
        and line == result.lines[-1]
    ):
        return True
    canonical = _canonical_line(line.text)
    return any(
        pattern not in {TOP_BAND_PATTERN, BOTTOM_BAND_PATTERN}
        and
        SequenceMatcher(None, canonical, pattern).ratio() >= 0.72
        for pattern in patterns
    )


def _strip_latin_artifacts(text: str) -> tuple[str, list[str]]:
    ethiopic_count = sum(_is_ethiopic(character) for character in text)
    if ethiopic_count < 8:
        return text, []

    removed: list[str] = []

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        removed.append(token)
        return ""

    cleaned = LATIN_ARTIFACT.sub(replace, text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
    return cleaned, removed


def _can_join_wrap(previous: OcrLine, current: OcrLine, width: int) -> bool:
    previous_word = previous.text.rsplit(maxsplit=1)[-1]
    current_word = current.text.split(maxsplit=1)[0]
    return (
        previous.right >= width * 0.80
        and current.left <= width * 0.22
        and 1 <= len(previous_word) <= 4
        and 1 <= len(current_word) <= 2
        and all(_is_ethiopic(character) for character in previous_word)
        and all(_is_ethiopic(character) for character in current_word)
    )


def _join_first_word(previous_text: str, current_text: str) -> tuple[str, str]:
    previous_prefix, separator, previous_word = previous_text.rpartition(" ")
    current_word, current_separator, current_remainder = current_text.partition(" ")
    joined = previous_word + current_word
    updated_previous = (
        f"{previous_prefix}{separator}{joined}" if separator else joined
    )
    return updated_previous, current_remainder if current_separator else ""


def clean_ocr_result(
    result: OcrResult,
    repeated_margin_patterns: tuple[str, ...] = (),
) -> CleanedPage:
    """Remove only auditable OCR noise and layout boilerplate."""
    retained: list[tuple[OcrLine, str]] = []
    removed: list[str] = []

    for line in result.lines:
        if _is_url(line.text) or _matches_repeated_margin(
            line, result, repeated_margin_patterns
        ):
            removed.append(line.text)
            continue
        cleaned_line, latin_removed = _strip_latin_artifacts(line.text)
        removed.extend(latin_removed)
        if cleaned_line:
            retained.append((line, cleaned_line))

    output_lines: list[str] = []
    output_layout: list[OcrLine] = []
    repaired = 0
    for line, text in retained:
        if output_lines and _can_join_wrap(
            output_layout[-1], line, result.image_width
        ):
            joined_previous, remainder = _join_first_word(output_lines[-1], text)
            output_lines[-1] = joined_previous
            repaired += 1
            if remainder:
                output_lines.append(remainder)
                output_layout.append(line)
            continue
        output_lines.append(text)
        output_layout.append(line)

    return CleanedPage(
        text="\n".join(output_lines).strip(),
        removed_fragments=tuple(removed),
        repaired_line_wraps=repaired,
    )


def assess_quality(
    text: str,
    mean_confidence: float | None,
    removed_fragment_count: int,
) -> QualityAssessment:
    visible = [character for character in text if not character.isspace()]
    letters = [character for character in visible if character.isalpha()]
    ethiopic = sum(_is_ethiopic(character) for character in letters)
    latin = sum(character.isascii() and character.isalpha() for character in letters)
    suspicious = sum(
        character == "\ufffd"
        or unicodedata.category(character) in {"Cc", "Cs", "Co", "Cn"}
        for character in visible
    )
    ethiopic_ratio = ethiopic / len(letters) if letters else 0.0
    latin_ratio = latin / len(letters) if letters else 0.0

    score = mean_confidence if mean_confidence is not None else 90.0
    flags: list[str] = []
    if len(visible) < 50:
        score -= 35
        flags.append("sparse_text")
    if mean_confidence is not None and mean_confidence < 75:
        score -= min(25, (75 - mean_confidence) * 0.8)
        flags.append("low_ocr_confidence")
    if ethiopic_ratio < 0.65 and len(letters) >= 20:
        score -= min(20, (0.65 - ethiopic_ratio) * 50)
        flags.append("low_ethiopic_ratio")
    if latin_ratio > 0.03 and ethiopic_ratio > 0.50:
        score -= min(15, latin_ratio * 60)
        flags.append("latin_artifacts")
    if latin_ratio > 0.10 and ethiopic_ratio > 0.50:
        flags.append("mixed_script_anomaly")
    if suspicious:
        score -= min(20, suspicious * 2)
        flags.append("suspicious_characters")
    if removed_fragment_count > max(5, len(visible) * 0.03):
        score -= 5
        flags.append("heavy_cleanup")

    score = round(max(0.0, min(100.0, score)), 2)
    if score < 75:
        flags.append("review_recommended")
    return QualityAssessment(
        score=score,
        mean_confidence=(
            round(mean_confidence, 2) if mean_confidence is not None else None
        ),
        visible_characters=len(visible),
        ethiopic_ratio=round(ethiopic_ratio, 4),
        latin_ratio=round(latin_ratio, 4),
        suspicious_characters=suspicious,
        removed_fragment_count=removed_fragment_count,
        flags=tuple(flags),
    )
