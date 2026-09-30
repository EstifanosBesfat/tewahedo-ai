"""PDF ingestion for text-based documents."""

from app.ingestion.extractor import EXTRACTION_METHOD, IngestionError, ingest_pdf
from app.ingestion.schemas import ExtractedDocument, PageText

__all__ = [
    "EXTRACTION_METHOD",
    "ExtractedDocument",
    "IngestionError",
    "PageText",
    "ingest_pdf",
]
