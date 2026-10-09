"""Swappable embedding providers with explicit token-limit handling."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

import numpy as np

from app.retrieval.schemas import EmbeddingBatch

E5_MODEL_NAME = "intfloat/multilingual-e5-small"
BGE_M3_MODEL_NAME = "BAAI/bge-m3"


class TokenLimitError(ValueError):
    """Raised when text cannot be embedded without silent truncation."""

    def __init__(self, token_length: int, max_tokens: int, text_kind: str) -> None:
        super().__init__(
            f"{text_kind} uses {token_length} tokens; model limit is "
            f"{max_tokens}"
        )
        self.token_length = token_length
        self.max_tokens = max_tokens
        self.text_kind = text_kind


class EmbeddingProvider(ABC):
    """Interface kept independent of any model or vector database."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Stable model identifier."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Maximum input tokens accepted without truncation."""

    @abstractmethod
    def document_token_lengths(self, texts: Sequence[str]) -> list[int]:
        """Return token counts including document-specific prompting."""

    @abstractmethod
    def embed_documents(self, texts: Sequence[str]) -> EmbeddingBatch:
        """Embed source chunks, explicitly handling every source token."""

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed one search query without silent truncation."""


class MultilingualE5SmallProvider(EmbeddingProvider):
    """Local multilingual E5-small inference with token-window pooling."""

    DOCUMENT_PREFIX = "passage: "
    QUERY_PREFIX = "query: "

    def __init__(
        self,
        device: str = "cpu",
        batch_size: int = 16,
        window_overlap_tokens: int = 32,
        model: Any | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if window_overlap_tokens < 0:
            raise ValueError("window_overlap_tokens cannot be negative")

        if model is None:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(E5_MODEL_NAME, device=device)

        self._model = model
        self._tokenizer = model.tokenizer
        self._batch_size = batch_size
        self._window_overlap_tokens = window_overlap_tokens
        self._max_tokens = int(model.max_seq_length)
        dimension = model.get_sentence_embedding_dimension()
        if dimension is None:
            raise ValueError("embedding model did not report its dimension")
        self._dimension = int(dimension)

    @property
    def model_name(self) -> str:
        return E5_MODEL_NAME

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    def _token_length(self, prefixed_text: str) -> int:
        encoded = self._tokenizer(
            prefixed_text,
            add_special_tokens=True,
            truncation=False,
        )
        return len(encoded["input_ids"])

    def document_token_lengths(self, texts: Sequence[str]) -> list[int]:
        return [
            self._token_length(f"{self.DOCUMENT_PREFIX}{text}")
            for text in texts
        ]

    def _document_windows(self, text: str) -> list[str]:
        prefix_tokens = len(
            self._tokenizer.encode(
                self.DOCUMENT_PREFIX,
                add_special_tokens=False,
            )
        )
        special_tokens = int(
            self._tokenizer.num_special_tokens_to_add(pair=False)
        )
        body_capacity = self.max_tokens - prefix_tokens - special_tokens
        if body_capacity < 1:
            raise ValueError("model token limit is too small for E5 prefix")
        stride = min(self._window_overlap_tokens, max(0, body_capacity - 1))

        encoded = self._tokenizer(
            text,
            add_special_tokens=False,
            truncation=False,
        )
        body_ids = encoded["input_ids"]
        if body_ids and isinstance(body_ids[0], list):
            body_ids = body_ids[0]
        if len(body_ids) <= body_capacity:
            token_windows = [body_ids]
        else:
            step = body_capacity - stride
            token_windows = []
            start = 0
            while start < len(body_ids):
                token_windows.append(body_ids[start : start + body_capacity])
                if start + body_capacity >= len(body_ids):
                    break
                start += step

        windows = [
            f"{self.DOCUMENT_PREFIX}"
            f"{self._tokenizer.decode(ids, skip_special_tokens=True).strip()}"
            for ids in token_windows
        ]
        for window in windows:
            length = self._token_length(window)
            if length > self.max_tokens:
                raise TokenLimitError(length, self.max_tokens, "passage window")
        return windows

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingBatch:
        source_texts = list(texts)
        if not source_texts:
            return EmbeddingBatch(
                vectors=[],
                token_lengths=[],
                window_counts=[],
            )

        token_lengths = self.document_token_lengths(source_texts)
        segment_texts: list[str] = []
        segment_owners: list[int] = []
        window_counts: list[int] = []
        for owner, (text, token_length) in enumerate(
            zip(source_texts, token_lengths, strict=True)
        ):
            if token_length <= self.max_tokens:
                windows = [f"{self.DOCUMENT_PREFIX}{text}"]
            else:
                windows = self._document_windows(text)
            window_counts.append(len(windows))
            segment_texts.extend(windows)
            segment_owners.extend([owner] * len(windows))

        segment_vectors = np.asarray(
            self._model.encode(
                segment_texts,
                batch_size=self._batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            ),
            dtype=np.float32,
        )

        vectors: list[list[float]] = []
        for owner in range(len(source_texts)):
            owned = segment_vectors[
                np.asarray(segment_owners, dtype=np.int32) == owner
            ]
            pooled = owned.mean(axis=0)
            norm = float(np.linalg.norm(pooled))
            if norm == 0:
                raise ValueError("embedding model returned a zero vector")
            vectors.append((pooled / norm).astype(float).tolist())

        return EmbeddingBatch(
            vectors=vectors,
            token_lengths=token_lengths,
            window_counts=window_counts,
        )

    def embed_query(self, query: str) -> list[float]:
        normalized = query.strip()
        if not normalized:
            raise ValueError("query must not be empty")
        prefixed = f"{self.QUERY_PREFIX}{normalized}"
        token_length = self._token_length(prefixed)
        if token_length > self.max_tokens:
            raise TokenLimitError(token_length, self.max_tokens, "query")
        vector = self._model.encode(
            [prefixed],
            batch_size=1,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        return np.asarray(vector, dtype=np.float32).astype(float).tolist()


class BgeM3DenseProvider(EmbeddingProvider):
    """Dense-only BGE-M3 embeddings.

    The model card says BGE-M3 no longer needs a query instruction. This
    provider therefore embeds the raw text and does not apply the E5
    ``query:`` or ``passage:`` prefixes. Sparse and multi-vector outputs
    are not requested. Vectors are L2-normalized so cosine similarity
    matches a dense dot product.
    """

    QUERY_PREFIX = ""
    DOCUMENT_PREFIX = ""

    def __init__(
        self,
        device: str = "cpu",
        batch_size: int = 1,
        model: Any | None = None,
        model_path: str | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if model is None:
            from sentence_transformers import SentenceTransformer

            source = model_path or BGE_M3_MODEL_NAME
            model = SentenceTransformer(
                source,
                device=device,
                local_files_only=model_path is not None,
            )

        self._model = model
        self._tokenizer = model.tokenizer
        self._batch_size = batch_size
        self._max_tokens = int(model.max_seq_length)
        self.library_prompts = {
            str(key): str(value)
            for key, value in dict(getattr(model, "prompts", {}) or {}).items()
        }
        self.default_prompt_name = getattr(model, "default_prompt_name", None)
        self._dimension = _embedding_dimension(model)

    @property
    def model_name(self) -> str:
        return BGE_M3_MODEL_NAME

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    def _token_length(self, text: str) -> int:
        encoded = self._tokenizer(
            text,
            add_special_tokens=True,
            truncation=False,
        )
        input_ids = encoded["input_ids"]
        if input_ids and isinstance(input_ids[0], list):
            input_ids = input_ids[0]
        return len(input_ids)

    def document_token_lengths(self, texts: Sequence[str]) -> list[int]:
        return [self._token_length(text) for text in texts]

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingBatch:
        if not texts:
            return EmbeddingBatch(vectors=[], token_lengths=[], window_counts=[])
        token_lengths = self.document_token_lengths(texts)
        for token_length in token_lengths:
            if token_length > self.max_tokens:
                raise TokenLimitError(token_length, self.max_tokens, "document")
        encoded = self._encode(list(texts))
        return EmbeddingBatch(
            vectors=[self._normalize(row) for row in encoded],
            token_lengths=token_lengths,
            window_counts=[1 for _ in texts],
        )

    def embed_query(self, query: str) -> list[float]:
        normalized = query.strip()
        if not normalized:
            raise ValueError("query must not be empty")
        token_length = self._token_length(normalized)
        if token_length > self.max_tokens:
            raise TokenLimitError(token_length, self.max_tokens, "query")
        return self._normalize(self._encode([normalized])[0])

    def _encode(self, texts: list[str]) -> np.ndarray:
        try:
            encoded = self._model.encode(
                texts,
                batch_size=self._batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
                prompt="",
            )
        except TypeError:
            encoded = self._model.encode(
                texts,
                batch_size=self._batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        array = np.asarray(encoded, dtype=np.float32)
        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.shape[0] != len(texts):
            raise ValueError("embedding model returned an unexpected batch size")
        return array

    @staticmethod
    def _normalize(vector: np.ndarray) -> list[float]:
        array = np.asarray(vector, dtype=np.float32)
        norm = float(np.linalg.norm(array))
        if norm == 0:
            raise ValueError("embedding model returned a zero vector")
        return (array / norm).astype(float).tolist()


def _embedding_dimension(model: Any) -> int:
    getter = getattr(model, "get_embedding_dimension", None)
    if getter is None:
        getter = model.get_sentence_embedding_dimension
    dimension = getter()
    if dimension is None:
        raise ValueError("embedding model did not report its dimension")
    return int(dimension)
