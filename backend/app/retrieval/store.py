"""Persistent Chroma storage for model-specific retrieval collections."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from app.preparation.schemas import PreparedChunk
from app.retrieval.schemas import SearchResult

E5_COLLECTION_NAME = "tewahedo_multilingual_e5_small_v1"


class ChromaVectorStore:
    """Chroma collection that receives embeddings from an external provider."""

    def __init__(
        self,
        persist_path: Path,
        collection_name: str,
        model_name: str,
        dimension: int,
        client: Any | None = None,
    ) -> None:
        if dimension < 1:
            raise ValueError("dimension must be positive")
        if client is None:
            import chromadb

            persist_path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(persist_path))

        self._client = client
        self.collection_name = collection_name
        self.model_name = model_name
        self.dimension = dimension
        self._collection = client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": model_name,
                "embedding_dimension": dimension,
            },
        )
        metadata = self._collection.metadata or {}
        existing_model = metadata.get("embedding_model")
        existing_dimension = metadata.get("embedding_dimension")
        if existing_model not in (None, model_name):
            raise ValueError(
                f"collection uses {existing_model}, not {model_name}"
            )
        if existing_dimension not in (None, dimension):
            raise ValueError(
                f"collection dimension is {existing_dimension}, not {dimension}"
            )

    @property
    def count(self) -> int:
        return int(self._collection.count())

    def upsert(
        self,
        chunks: Sequence[PreparedChunk],
        vectors: Sequence[Sequence[float]],
        batch_size: int = 32,
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunk and vector counts must match")
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        for vector in vectors:
            if len(vector) != self.dimension:
                raise ValueError(
                    f"expected {self.dimension}-dimensional vectors"
                )

        for start in range(0, len(chunks), batch_size):
            chunk_batch = chunks[start : start + batch_size]
            vector_batch = vectors[start : start + batch_size]
            self._collection.upsert(
                ids=[chunk.chunk_id for chunk in chunk_batch],
                embeddings=[list(vector) for vector in vector_batch],
                documents=[chunk.text for chunk in chunk_batch],
                metadatas=[
                    {
                        "document_id": chunk.document_id,
                        "chunk_id": chunk.chunk_id,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "extraction_method": chunk.extraction_method,
                        "source_quality_score": chunk.source_quality_score,
                    }
                    for chunk in chunk_batch
                ],
            )

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int,
    ) -> list[SearchResult]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        if len(query_vector) != self.dimension:
            raise ValueError(
                f"expected a {self.dimension}-dimensional query vector"
            )
        if self.count == 0:
            return []

        result = self._collection.query(
            query_embeddings=[list(query_vector)],
            n_results=min(top_k, self.count),
            include=["documents", "metadatas", "distances"],
        )
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        hits: list[SearchResult] = []
        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
            strict=True,
        ):
            similarity = max(-1.0, min(1.0, 1.0 - float(distance)))
            hits.append(
                SearchResult(
                    similarity_score=similarity,
                    document_id=str(metadata["document_id"]),
                    chunk_id=str(metadata["chunk_id"]),
                    page_start=int(metadata["page_start"]),
                    page_end=int(metadata["page_end"]),
                    text=str(document),
                    extraction_method=str(metadata["extraction_method"]),
                    source_quality_score=float(
                        metadata["source_quality_score"]
                    ),
                )
            )
        return hits
