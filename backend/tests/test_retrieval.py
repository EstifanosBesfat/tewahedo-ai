"""Tests for model-independent retrieval and multilingual E5 handling."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Sequence

import pytest

from app.preparation.schemas import (
    ChunkingConfig,
    PreparedChunk,
    PreparedDocument,
)
from app.retrieval.embeddings import (
    EmbeddingProvider,
    MultilingualE5SmallProvider,
    TokenLimitError,
)
from app.retrieval.evaluation import score_relevance_audit
from app.retrieval.schemas import (
    EmbeddingBatch,
    EvaluationQuestionSet,
    EvaluationRun,
    RetrievalAudit,
)
from app.retrieval.service import RetrievalService
from app.retrieval.store import ChromaVectorStore


class FakeTokenizer:
    def __init__(self) -> None:
        self._vocabulary: dict[str, int] = {}
        self._reverse: dict[int, str] = {}

    def _ids(self, text: str) -> list[int]:
        ids: list[int] = []
        for word in text.split():
            if word not in self._vocabulary:
                token_id = len(self._vocabulary) + 10
                self._vocabulary[word] = token_id
                self._reverse[token_id] = word
            ids.append(self._vocabulary[word])
        return ids

    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
    ) -> list[int]:
        ids = self._ids(text)
        return [1, *ids, 2] if add_special_tokens else ids

    def num_special_tokens_to_add(self, pair: bool = False) -> int:
        return 2

    def decode(
        self,
        ids: Sequence[int],
        skip_special_tokens: bool = True,
    ) -> str:
        return " ".join(self._reverse[token_id] for token_id in ids)

    def __call__(
        self,
        text: str,
        add_special_tokens: bool,
        truncation: bool,
        max_length: int | None = None,
        stride: int = 0,
        return_overflowing_tokens: bool = False,
    ) -> dict[str, list[int] | list[list[int]]]:
        ids = self._ids(text)
        if truncation and return_overflowing_tokens:
            assert max_length is not None
            windows: list[list[int]] = []
            start = 0
            while start < len(ids):
                windows.append(ids[start : start + max_length])
                if start + max_length >= len(ids):
                    break
                start += max_length - stride
            return {"input_ids": windows}
        if add_special_tokens:
            ids = [1, *ids, 2]
        return {"input_ids": ids}


class FakeSentenceTransformer:
    def __init__(self) -> None:
        self.tokenizer = FakeTokenizer()
        self.max_seq_length = 8
        self.encoded_texts: list[str] = []

    def get_sentence_embedding_dimension(self) -> int:
        return 3

    def encode(self, texts: Sequence[str], **_: object) -> list[list[float]]:
        self.encoded_texts.extend(texts)
        vectors = []
        for text in texts:
            if text.startswith("query:"):
                vectors.append([1.0, 0.0, 0.0])
            else:
                vectors.append([0.0, 1.0, 0.0])
        return vectors


class KeywordEmbeddingProvider(EmbeddingProvider):
    @property
    def model_name(self) -> str:
        return "test-keyword-model"

    @property
    def dimension(self) -> int:
        return 3

    @property
    def max_tokens(self) -> int:
        return 512

    def document_token_lengths(self, texts: Sequence[str]) -> list[int]:
        return [len(text.split()) + 2 for text in texts]

    def _vector(self, text: str) -> list[float]:
        if "ሰንበት" in text:
            vector = [1.0, 0.0, 0.0]
        elif "ገንዘብ" in text:
            vector = [0.0, 1.0, 0.0]
        else:
            vector = [0.0, 0.0, 1.0]
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector]

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingBatch:
        lengths = self.document_token_lengths(texts)
        return EmbeddingBatch(
            vectors=[self._vector(text) for text in texts],
            token_lengths=lengths,
            window_counts=[1] * len(texts),
        )

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("query must not be empty")
        return self._vector(query)


def _prepared_document() -> PreparedDocument:
    chunks = [
        PreparedChunk(
            chunk_id="sample:chunk-0001",
            document_id="sample",
            page_start=3,
            page_end=4,
            text="ሰንበት ለሰው የተሰጠ የዕረፍት ቀን ነው።",
            extraction_method="ocr",
            source_quality_score=82.5,
        ),
        PreparedChunk(
            chunk_id="sample:chunk-0002",
            document_id="sample",
            page_start=7,
            page_end=7,
            text="ገንዘብን እንደ ጣዖት ማምለክ አይገባም።",
            extraction_method="ocr",
            source_quality_score=76.25,
        ),
    ]
    return PreparedDocument(
        document_id="sample",
        source_filename="sample.pdf",
        source_page_count=7,
        chunking=ChunkingConfig(target_chars=1200, overlap_chars=150),
        chunk_count=len(chunks),
        chunks=chunks,
    )


def test_e5_uses_required_prefixes_and_windows_over_limit_text() -> None:
    model = FakeSentenceTransformer()
    provider = MultilingualE5SmallProvider(
        model=model,
        window_overlap_tokens=1,
    )

    short = provider.embed_documents(["አጭር ጽሑፍ"])
    query_vector = provider.embed_query("ሰንበት ምንድን ነው?")
    long = provider.embed_documents([" ".join(["ረጅም"] * 15)])

    assert short.window_counts == [1]
    assert long.token_lengths[0] > provider.max_tokens
    assert long.window_counts[0] > 1
    assert query_vector == [1.0, 0.0, 0.0]
    assert model.encoded_texts[0].startswith("passage: ")
    assert model.encoded_texts[1].startswith("query: ")
    assert all(
        text.startswith("passage: ")
        for text in model.encoded_texts[2:]
    )
    assert all(
        provider._token_length(text) <= provider.max_tokens
        for text in model.encoded_texts
    )


def test_e5_rejects_query_over_token_limit() -> None:
    provider = MultilingualE5SmallProvider(model=FakeSentenceTransformer())

    with pytest.raises(TokenLimitError, match="model limit"):
        provider.embed_query(" ".join(["ጥያቄ"] * 20))


def test_indexes_searches_and_preserves_all_provenance(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "sample.chunks.json"
    source_path.write_text(
        _prepared_document().model_dump_json(indent=2),
        encoding="utf-8",
    )
    source_before = source_path.read_bytes()
    provider = KeywordEmbeddingProvider()
    store = ChromaVectorStore(
        persist_path=tmp_path / "chroma",
        collection_name="test_amharic_retrieval",
        model_name=provider.model_name,
        dimension=provider.dimension,
    )
    service = RetrievalService(provider, store)

    first_report = service.index_document(source_path)
    second_report = service.index_document(source_path)
    results = service.search("ሰንበት ለምን ተሰጠ?", top_k=2)

    assert source_path.read_bytes() == source_before
    assert first_report.indexed_chunks == 2
    assert second_report.collection_count == 2
    assert store.count == 2
    assert results[0].chunk_id == "sample:chunk-0001"
    assert results[0].document_id == "sample"
    assert (results[0].page_start, results[0].page_end) == (3, 4)
    assert results[0].extraction_method == "ocr"
    assert results[0].source_quality_score == 82.5
    assert results[0].text == _prepared_document().chunks[0].text
    assert results[0].similarity_score > results[1].similarity_score


@pytest.mark.parametrize(
    ("query", "top_k"),
    [
        ("", 5),
        ("   ", 5),
        ("ሰንበት", 0),
        ("ሰንበት", -1),
    ],
)
def test_rejects_empty_or_invalid_search(
    tmp_path: Path,
    query: str,
    top_k: int,
) -> None:
    provider = KeywordEmbeddingProvider()
    store = ChromaVectorStore(
        persist_path=tmp_path / "chroma",
        collection_name="test_invalid_query",
        model_name=provider.model_name,
        dimension=provider.dimension,
    )
    service = RetrievalService(provider, store)

    with pytest.raises(ValueError):
        service.search(query, top_k)


def test_evaluation_question_file_has_five_questions_per_category() -> None:
    questions_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "evaluation"
        / "amharic_retrieval_questions.json"
    )

    question_set = EvaluationQuestionSet.model_validate_json(
        questions_path.read_text(encoding="utf-8")
    )

    assert len(question_set.questions) == 15
    assert {
        category: sum(
            question.category == category
            for question in question_set.questions
        )
        for category in ("direct", "paraphrased", "conceptual")
    } == {"direct": 5, "paraphrased": 5, "conceptual": 5}


def test_retrieval_audit_recall_uses_only_verified_chunks() -> None:
    evaluation_dir = (
        Path(__file__).resolve().parents[1] / "data" / "evaluation"
    )
    chunks_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "processed"
        / "10commandments.chunks.json"
    )
    audit = RetrievalAudit.model_validate_json(
        (evaluation_dir / "retrieval-audit.json").read_text(encoding="utf-8")
    )
    run = EvaluationRun.model_validate_json(
        (evaluation_dir / "multilingual-e5-small.results.json").read_text(
            encoding="utf-8"
        )
    )
    chunks = {
        chunk["chunk_id"]: chunk
        for chunk in json.loads(chunks_path.read_text(encoding="utf-8"))["chunks"]
    }

    assert len(audit.judgments) == 15
    assert audit.model_scores[0].metric_eligible_count == 14
    assert audit.model_scores[0].excluded_question_ids == ["direct-01"]
    assert audit.model_scores[0].recall_at_3.hits == 9
    assert audit.model_scores[0].recall_at_5.hits == 12
    assert audit.model_scores[0].recall_at_3.eligible == 14
    recomputed = score_relevance_audit(
        audit.judgments,
        run,
        "multilingual-e5-small.results.json",
    )
    assert recomputed.model_dump(mode="json") == audit.model_scores[0].model_dump(
        mode="json"
    )

    first = next(
        judgment
        for judgment in audit.judgments
        if judgment.question_id == "direct-01"
    )
    assert first.metric_eligible is False
    assert not any(chunk.status == "verified" for chunk in first.chunks)
    assert "10commandments:chunk-0008" not in (
        audit.model_scores[0]
        .questions["direct-01"]
        .documented_sense_chunk_ids_in_top_5
    )

    for judgment in audit.judgments:
        for item in judgment.chunks:
            source = chunks[item.chunk_id]
            assert item.page_start == source["page_start"]
            assert item.page_end == source["page_end"]

    for result in run.results:
        for hit in result.top_5:
            source = chunks[hit.chunk_id]
            assert hit.document_id == source["document_id"]
            assert hit.page_start == source["page_start"]
            assert hit.page_end == source["page_end"]
            assert hit.text == source["text"]
            assert hit.extraction_method == source["extraction_method"]
            assert hit.source_quality_score == source["source_quality_score"]

    windows = audit.over_limit_window_audit
    assert windows.over_limit_chunk_count == 30
    assert windows.window_counts == [2]
    assert all(chunk.window_count == 2 for chunk in windows.chunks)
    assert windows.provenance_mismatches == 0
