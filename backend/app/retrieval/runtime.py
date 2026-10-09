"""Default local runtime wiring for the multilingual E5 experiment."""

from __future__ import annotations

from pathlib import Path

from app.retrieval.embeddings import BgeM3DenseProvider, MultilingualE5SmallProvider
from app.retrieval.service import RetrievalService
from app.retrieval.store import (
    BGE_M3_COLLECTION_NAME,
    E5_COLLECTION_NAME,
    ChromaVectorStore,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VECTOR_STORE_PATH = (
    BACKEND_ROOT / "data" / "vectorstore" / "multilingual-e5-small"
)
DEFAULT_BGE_M3_VECTOR_STORE_PATH = (
    BACKEND_ROOT / "data" / "vectorstore" / "bge-m3-units"
)


def create_e5_service(
    persist_path: Path = DEFAULT_VECTOR_STORE_PATH,
    device: str = "cpu",
    model_path: Path | None = None,
) -> RetrievalService:
    local_model = None
    if model_path is not None:
        from sentence_transformers import SentenceTransformer

        local_model = SentenceTransformer(
            str(model_path),
            device=device,
            local_files_only=True,
        )
    provider = MultilingualE5SmallProvider(device=device, model=local_model)
    store = ChromaVectorStore(
        persist_path=persist_path,
        collection_name=E5_COLLECTION_NAME,
        model_name=provider.model_name,
        dimension=provider.dimension,
    )
    return RetrievalService(provider, store)


def create_bge_m3_service(
    persist_path: Path = DEFAULT_BGE_M3_VECTOR_STORE_PATH,
    device: str = "cpu",
    model_path: Path | None = None,
    batch_size: int = 1,
) -> RetrievalService:
    e5_unit_store = (
        BACKEND_ROOT / "data" / "vectorstore" / "multilingual-e5-small-units"
    )
    blocked = {
        DEFAULT_VECTOR_STORE_PATH.resolve(),
        e5_unit_store.resolve(),
    }
    if persist_path.resolve() in blocked:
        raise ValueError("BGE-M3 cannot use an E5 vector-store directory")
    if BGE_M3_COLLECTION_NAME == E5_COLLECTION_NAME:
        raise ValueError("BGE-M3 cannot use the E5 collection name")
    provider = BgeM3DenseProvider(
        device=device,
        batch_size=batch_size,
        model_path=str(model_path) if model_path is not None else None,
    )
    store = ChromaVectorStore(
        persist_path=persist_path,
        collection_name=BGE_M3_COLLECTION_NAME,
        model_name=provider.model_name,
        dimension=provider.dimension,
    )
    return RetrievalService(provider, store)
