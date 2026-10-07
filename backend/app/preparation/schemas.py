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


class RetrievalUnit(BaseModel):
    """A smaller retrieval span derived from one prepared chunk."""

    chunk_id: str
    document_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    text: str = Field(min_length=1)
    extraction_method: str
    source_quality_score: float = Field(ge=0, le=100)
    parent_chunk_id: str
    parent_page_start: int = Field(ge=1)
    parent_page_end: int = Field(ge=1)
    token_length: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_page_range(self) -> "RetrievalUnit":
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        if self.parent_page_end < self.parent_page_start:
            raise ValueError("parent page range is invalid")
        return self


class RetrievalUnitDocument(BaseModel):
    """Retrieval units for one document, traced to the prepared chunks."""

    document_id: str
    source_filename: str
    parent_chunk_count: int = Field(ge=0)
    max_tokens: int = Field(ge=1)
    unit_count: int = Field(ge=0)
    units: list[RetrievalUnit]

    @model_validator(mode="after")
    def validate_unit_count(self) -> "RetrievalUnitDocument":
        if self.unit_count != len(self.units):
            raise ValueError("unit_count must match the number of units")
        return self
