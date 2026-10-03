"""Content and rendered-page similarity checks for source PDFs."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

import pymupdf
from PIL import Image


@dataclass(frozen=True)
class DocumentSimilarity:
    filenames: tuple[str, str]
    same_pdf_bytes: bool
    page_counts: tuple[int, int]
    same_page_count: bool
    body_text_similarity: float
    mean_corresponding_page_image_similarity: float
    near_identical_rendered_pages: int
    duplicate: bool
    conclusion: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_body_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    lines = []
    for line in normalized.splitlines():
        compact = "".join(character for character in line if character.isalnum())
        if "ethiopianorthodox" in compact:
            continue
        if (
            "ethiopianorthodoxtewahidochurch" in compact
            or "faithandorder" in compact
        ):
            continue
        lines.append(line)
    return re.sub(r"\s+", "", "\n".join(lines))


def _ngrams(text: str, size: int = 5) -> set[str]:
    if len(text) < size:
        return {text} if text else set()
    return {text[index : index + size] for index in range(len(text) - size + 1)}


def body_text_similarity(first: str, second: str) -> float:
    first_ngrams = _ngrams(normalize_body_text(first))
    second_ngrams = _ngrams(normalize_body_text(second))
    if not first_ngrams and not second_ngrams:
        return 1.0
    union = first_ngrams | second_ngrams
    return len(first_ngrams & second_ngrams) / len(union) if union else 0.0


def _difference_hash(page: pymupdf.Page, size: int = 16) -> int:
    pixmap = page.get_pixmap(dpi=96, colorspace=pymupdf.csGRAY, alpha=False)
    image = Image.frombytes("L", (pixmap.width, pixmap.height), pixmap.samples)
    try:
        resized = image.resize((size + 1, size), Image.Resampling.LANCZOS)
        pixels = list(resized.get_flattened_data())
    finally:
        image.close()
    result = 0
    for row in range(size):
        offset = row * (size + 1)
        for column in range(size):
            result = (result << 1) | int(
                pixels[offset + column] > pixels[offset + column + 1]
            )
    return result


def _hash_similarity(first: int, second: int, bits: int = 256) -> float:
    return 1.0 - ((first ^ second).bit_count() / bits)


def compare_documents(
    first_path: Path,
    second_path: Path,
    first_text: str,
    second_text: str,
) -> DocumentSimilarity:
    """Compare bytes, rendered corresponding pages, and body content."""
    with pymupdf.open(first_path) as first_document, pymupdf.open(
        second_path
    ) as second_document:
        first_count = len(first_document)
        second_count = len(second_document)
        corresponding = min(first_count, second_count)
        image_similarities = [
            _hash_similarity(
                _difference_hash(first_document[index]),
                _difference_hash(second_document[index]),
            )
            for index in range(corresponding)
        ]

    text_similarity = body_text_similarity(first_text, second_text)
    mean_image_similarity = (
        sum(image_similarities) / len(image_similarities)
        if image_similarities
        else 0.0
    )
    near_identical = sum(value >= 0.98 for value in image_similarities)
    same_bytes = _sha256(first_path) == _sha256(second_path)
    same_page_count = first_count == second_count
    duplicate = same_bytes or (
        same_page_count
        and first_count > 0
        and near_identical == first_count
        and text_similarity >= 0.95
    )
    conclusion = (
        "duplicate documents"
        if duplicate
        else "separate documents with distinct body content and/or pages"
    )
    return DocumentSimilarity(
        filenames=(first_path.name, second_path.name),
        same_pdf_bytes=same_bytes,
        page_counts=(first_count, second_count),
        same_page_count=same_page_count,
        body_text_similarity=round(text_similarity, 4),
        mean_corresponding_page_image_similarity=round(mean_image_similarity, 4),
        near_identical_rendered_pages=near_identical,
        duplicate=duplicate,
        conclusion=conclusion,
    )
