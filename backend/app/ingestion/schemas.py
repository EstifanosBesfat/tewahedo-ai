"""Metadata saved with extracted PDF text."""

from typing import Literal

from pydantic import BaseModel, Field

ExtractionMethod = Literal["pymupdf", "ocr"]


class PageText(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    extraction_method: ExtractionMethod
    raw_text: str
    pymupdf_text: str


class ExtractedDocument(BaseModel):
    filename: str
    page_count: int = Field(ge=0)
    extraction_method: Literal["pymupdf", "ocr", "mixed"]
    encoding: str
    pages: list[PageText]


class IngestRequest(BaseModel):
    filename: str = Field(min_length=1)
