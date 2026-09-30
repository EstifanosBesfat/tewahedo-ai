"""FastAPI entrypoint for document ingestion."""

from fastapi import FastAPI, HTTPException

from app.ingestion.extractor import IngestionError, ingest_pdf
from app.ingestion.schemas import ExtractedDocument, IngestRequest

app = FastAPI(
    title="Tewahedo AI",
    version="0.1.0",
    description=(
        "Document ingestion for the Amharic Ethiopian Orthodox Tewahedo "
        "knowledge assistant."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=ExtractedDocument)
def ingest_document(body: IngestRequest) -> ExtractedDocument:
    try:
        document, _output_path = ingest_pdf(body.filename)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return document
