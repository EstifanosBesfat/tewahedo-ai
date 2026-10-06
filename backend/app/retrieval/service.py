"""Indexing and semantic-search orchestration."""

from __future__ import annotations

from pathlib import Path

from app.preparation.schemas import PreparedDocument
from app.retrieval.embeddings import EmbeddingProvider
from app.retrieval.schemas import IndexingReport, SearchResult, TokenLimitItem
from app.retrieval.store import ChromaVectorStore


class RetrievalService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_document(self, source_path: Path) -> IndexingReport:
        document = PreparedDocument.model_validate_json(
            source_path.read_text(encoding="utf-8")
        )
        texts = [chunk.text for chunk in document.chunks]
        batch = self.embedding_provider.embed_documents(texts)
        self.vector_store.upsert(document.chunks, batch.vectors)

        token_lengths = batch.token_lengths
        over_limit = [
            TokenLimitItem(
                identifier=chunk.chunk_id,
                token_length=token_length,
                window_count=window_count,
            )
            for chunk, token_length, window_count in zip(
                document.chunks,
                token_lengths,
                batch.window_counts,
                strict=True,
            )
            if token_length > self.embedding_provider.max_tokens
        ]
        return IndexingReport(
            model_name=self.embedding_provider.model_name,
            collection_name=self.vector_store.collection_name,
            source_path=str(source_path),
            requested_chunks=len(document.chunks),
            indexed_chunks=len(batch.vectors),
            collection_count=self.vector_store.count,
            max_model_tokens=self.embedding_provider.max_tokens,
            minimum_token_length=min(token_lengths, default=0),
            maximum_token_length=max(token_lengths, default=0),
            over_limit_chunks=over_limit,
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        normalized = query.strip()
        if not normalized:
            raise ValueError("query must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        query_vector = self.embedding_provider.embed_query(normalized)
        return self.vector_store.search(query_vector, top_k)
