"""Default local runtime wiring for the multilingual E5 experiment."""

from __future__ import annotations

from pathlib import Path

from app.retrieval.embeddings import MultilingualE5SmallProvider
from app.retrieval.service import RetrievalService
from app.retrieval.store import E5_COLLECTION_NAME, ChromaVectorStore

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VECTOR_STORE_PATH = (
    BACKEND_ROOT / "data" / "vectorstore" / "multilingual-e5-small"
)


def create_e5_service(
    persist_path: Path = DEFAULT_VECTOR_STORE_PATH,
    device: str = "cpu",
) -> RetrievalService:
    provider = MultilingualE5SmallProvider(device=device)
    store = ChromaVectorStore(
        persist_path=persist_path,
        collection_name=E5_COLLECTION_NAME,
        model_name=provider.model_name,
        dimension=provider.dimension,
    )
    return RetrievalService(provider, store)
