"""Metadata saved with extracted PDF text."""

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int = Field(ge=1)
    text: str


class ExtractedDocument(BaseModel):
    filename: str
    page_count: int = Field(ge=0)
    extraction_method: str
    encoding: str
    pages: list[PageText]


class IngestRequest(BaseModel):
    filename: str = Field(min_length=1)
