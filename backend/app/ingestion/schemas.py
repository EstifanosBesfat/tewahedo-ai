"""Metadata saved with extracted PDF text."""

from typing import Literal

from pydantic import BaseModel, Field

ExtractionMethod = Literal["pymupdf", "ocr"]


class OcrMetadata(BaseModel):
    language: str
    dpi: int = Field(ge=1)
    psm: int = Field(ge=0)
    preprocessing: str
    mean_confidence: float | None = Field(default=None, ge=0, le=100)


class PageQuality(BaseModel):
    score: float = Field(ge=0, le=100)
    mean_confidence: float | None = Field(default=None, ge=0, le=100)
    visible_characters: int = Field(ge=0)
    ethiopic_ratio: float = Field(ge=0, le=1)
    latin_ratio: float = Field(ge=0, le=1)
    suspicious_characters: int = Field(ge=0)
    removed_fragment_count: int = Field(ge=0)
    flags: list[str] = Field(default_factory=list)


class PageText(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    extraction_method: ExtractionMethod
    raw_text: str
    pymupdf_text: str
    ocr: OcrMetadata | None = None
    removed_fragments: list[str] = Field(default_factory=list)
    repaired_line_wraps: int = Field(default=0, ge=0)
    quality: PageQuality


class ExtractedDocument(BaseModel):
    filename: str
    page_count: int = Field(ge=0)
    extraction_method: Literal["pymupdf", "ocr", "mixed"]
    encoding: str
    pages: list[PageText]
    quality_summary: dict[str, int | float]


class IngestRequest(BaseModel):
    filename: str = Field(min_length=1)
