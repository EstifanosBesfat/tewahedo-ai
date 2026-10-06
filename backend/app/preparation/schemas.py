"""Schemas for deterministic, post-extraction text preparation."""

from pydantic import BaseModel, Field, model_validator


class ChunkingConfig(BaseModel):
    """Character-based sizing used before an embedding tokenizer is selected."""

    target_chars: int = Field(default=1200, ge=200)
    overlap_chars: int = Field(default=150, ge=0)

    @model_validator(mode="after")
    def validate_overlap(self) -> "ChunkingConfig":
        if self.overlap_chars >= self.target_chars:
            raise ValueError("overlap_chars must be smaller than target_chars")
        return self


class PreparedChunk(BaseModel):
    """One embedding-ready chunk with source provenance."""

    chunk_id: str
    document_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    text: str = Field(min_length=1)
    extraction_method: str
    source_quality_score: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_page_range(self) -> "PreparedChunk":
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        return self


class PreparedDocument(BaseModel):
    """Chunk output written to data/processed without changing extraction data."""

    document_id: str
    source_filename: str
    source_page_count: int = Field(ge=0)
    chunking: ChunkingConfig
    chunk_count: int = Field(ge=0)
    chunks: list[PreparedChunk]

    @model_validator(mode="after")
    def validate_chunk_count(self) -> "PreparedDocument":
        if self.chunk_count != len(self.chunks):
            raise ValueError("chunk_count must match the number of chunks")
        return self
