"""BGE-M3 configuration, store isolation, and frozen-evaluation compatibility."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from app.preparation.schemas import PreparedChunk
from app.retrieval.embeddings import (
    BGE_M3_MODEL_NAME,
    E5_MODEL_NAME,
    BgeM3DenseProvider,
    TokenLimitError,
)
from app.retrieval.evaluation import (
    collapse_units_to_parents,
    score_parent_recall,
)
from app.retrieval.runtime import (
    DEFAULT_BGE_M3_VECTOR_STORE_PATH,
    DEFAULT_VECTOR_STORE_PATH,
    create_bge_m3_service,
)
from app.retrieval.store import (
    BGE_M3_COLLECTION_NAME,
    E5_COLLECTION_NAME,
    ChromaVectorStore,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH_PATH = BACKEND_ROOT / "data" / "evaluation" / "ground-truth-v3.json"
E5_RESULTS_PATH = BACKEND_ROOT / "data" / "evaluation" / "retrieval-evaluation-v3.json"
UNITS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.retrieval-units.json"


class FakeTokenizer:
    def __call__(self, text: str, add_special_tokens: bool = True, truncation: bool = False):
        extra = 2 if add_special_tokens else 0
        return {"input_ids": [1] * (len(text.split()) + extra)}


class RecordingModel:
    def __init__(self, vector: list[float], max_seq_length: int = 32) -> None:
        self.max_seq_length = max_seq_length
        self.tokenizer = FakeTokenizer()
        self.prompts = {"query": "", "document": ""}
        self.default_prompt_name = None
        self.calls: list[dict[str, object]] = []
        self._vector = vector

    def get_sentence_embedding_dimension(self) -> int:
        return len(self._vector)

    def encode(self, texts: list[str], **kwargs: object) -> list[list[float]]:
        self.calls.append({"texts": list(texts), "prompt": kwargs.get("prompt")})
        return [self._vector for _ in texts]


def _chunk(chunk_id: str) -> PreparedChunk:
    return PreparedChunk(
        chunk_id=chunk_id,
        document_id="10commandments",
        page_start=1,
        page_end=1,
        text="የሙከራ ጽሑፍ",
        extraction_method="ocr",
        source_quality_score=80,
    )


def test_bge_m3_embeds_raw_text_and_normalizes() -> None:
    model = RecordingModel([3.0, 0.0, 0.0, 0.0])
    provider = BgeM3DenseProvider(model=model)

    assert provider.model_name == BGE_M3_MODEL_NAME
    assert provider.dimension == 4
    assert provider.QUERY_PREFIX == ""
    assert provider.DOCUMENT_PREFIX == ""

    document = provider.embed_documents(["በሐሰት አትመስክር"])
    query = provider.embed_query("  በባልንጀራ ላይ ሐሰት ምስክር  ")

    assert model.calls[0]["texts"] == ["በሐሰት አትመስክር"]
    assert model.calls[0]["prompt"] == ""
    assert model.calls[1]["texts"] == ["በባልንጀራ ላይ ሐሰት ምስክር"]
    assert model.calls[1]["prompt"] == ""
    assert document.window_counts == [1]
    np.testing.assert_allclose(document.vectors[0], [1.0, 0.0, 0.0, 0.0])
    np.testing.assert_allclose(query, [1.0, 0.0, 0.0, 0.0])


def test_bge_m3_refuses_silent_truncation() -> None:
    model = RecordingModel([1.0, 0.0], max_seq_length=4)
    provider = BgeM3DenseProvider(model=model)

    with pytest.raises(TokenLimitError):
        provider.embed_documents(["one two three four five"])

    assert model.calls == []


def test_bge_m3_store_is_isolated_from_e5(tmp_path: Path) -> None:
    import chromadb

    bge_client = chromadb.PersistentClient(path=str(tmp_path / "bge"))
    e5_client = chromadb.PersistentClient(path=str(tmp_path / "e5"))
    bge_store = ChromaVectorStore(
        persist_path=tmp_path / "bge",
        collection_name=BGE_M3_COLLECTION_NAME,
        model_name=BGE_M3_MODEL_NAME,
        dimension=4,
        client=bge_client,
    )
    e5_store = ChromaVectorStore(
        persist_path=tmp_path / "e5",
        collection_name=E5_COLLECTION_NAME,
        model_name="intfloat/multilingual-e5-small",
        dimension=3,
        client=e5_client,
    )
    bge_store.upsert([_chunk("10commandments:chunk-0001:unit-01")], [[1, 0, 0, 0]])

    assert bge_store.count == 1
    assert e5_store.count == 0
    assert bge_store.stored_ids() == {"10commandments:chunk-0001:unit-01"}
    assert BGE_M3_COLLECTION_NAME != E5_COLLECTION_NAME
    assert DEFAULT_BGE_M3_VECTOR_STORE_PATH != DEFAULT_VECTOR_STORE_PATH
    assert DEFAULT_BGE_M3_VECTOR_STORE_PATH.name == "bge-m3-units"

    with pytest.raises(ValueError, match="intfloat/multilingual-e5-small"):
        ChromaVectorStore(
            persist_path=tmp_path / "bge",
            collection_name=BGE_M3_COLLECTION_NAME,
            model_name="intfloat/multilingual-e5-small",
            dimension=4,
            client=bge_client,
        )


def test_bge_service_refuses_e5_directories_before_loading_a_model() -> None:
    with pytest.raises(ValueError, match="E5"):
        create_bge_m3_service(persist_path=DEFAULT_VECTOR_STORE_PATH)
    with pytest.raises(ValueError, match="E5"):
        create_bge_m3_service(
            persist_path=DEFAULT_VECTOR_STORE_PATH.parent
            / "multilingual-e5-small-units"
        )


def test_parent_collapse_keeps_first_unique_parents() -> None:
    unit_ids = [
        "10commandments:chunk-0001:unit-01",
        "10commandments:chunk-0001:unit-02",
        "10commandments:chunk-0002:unit-01",
        "10commandments:chunk-0003:unit-01",
        "10commandments:chunk-0004:unit-01",
        "10commandments:chunk-0005:unit-01",
        "10commandments:chunk-0006:unit-01",
    ]

    assert collapse_units_to_parents(unit_ids, width=5) == [
        "10commandments:chunk-0001",
        "10commandments:chunk-0002",
        "10commandments:chunk-0003",
        "10commandments:chunk-0004",
        "10commandments:chunk-0005",
    ]


def test_either_relevant_parent_counts_and_excluded_question_does_not() -> None:
    questions = [
        {
            "question_id": "direct-01",
            "question_type": "direct",
            "metric_eligible": False,
            "relevant_chunk_ids": [],
            "exclusion_reason": "ambiguous",
        },
        {
            "question_id": "sample",
            "question_type": "direct",
            "metric_eligible": True,
            "relevant_chunk_ids": [
                "10commandments:chunk-0085",
                "10commandments:chunk-0089",
            ],
        },
    ]
    scored = score_parent_recall(
        questions,
        {
            "direct-01": ["10commandments:chunk-0008"],
            "sample": ["10commandments:chunk-0089", "10commandments:chunk-0001"],
        },
    )

    assert scored["eligible"] == 1
    assert scored["hits"] == {1: 1, 3: 1, 5: 1}
    assert scored["misses_at_5"] == []
    sample = scored["questions"][1]
    assert sample["first_relevant_parent_rank"] == 1
    assert sample["top_1"] is True


def test_frozen_e5_v3_results_match_the_parent_recall_rule() -> None:
    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
    e5_results = json.loads(E5_RESULTS_PATH.read_text(encoding="utf-8"))
    units = json.loads(UNITS_PATH.read_text(encoding="utf-8"))

    assert e5_results["model_name"] == "intfloat/multilingual-e5-small"
    assert e5_results["recall_at_1"] == "9/14"
    assert e5_results["recall_at_3"] == "12/14"
    assert e5_results["recall_at_5"] == "13/14"
    assert e5_results["misses_at_5"] == ["direct-05"]
    assert e5_results["unit_count"] == 182
    assert units["unit_count"] == 182
    assert ground_truth["metric_eligible_count"] == 14
    assert ground_truth["excluded_question_ids"] == ["direct-01"]

    parents_by_question = {}
    for question in e5_results["questions"]:
        unit_ids = [row["unit_id"] for row in question["unit_ranking"]]
        collapsed = collapse_units_to_parents(unit_ids, width=5)
        stored = [row["parent_chunk_id"] for row in question["parent_ranking"]]
        assert collapsed == stored
        parents_by_question[question["question_id"]] = stored

    scored = score_parent_recall(ground_truth["questions"], parents_by_question)
    assert scored["hits"] == {1: 9, 3: 12, 5: 13}
    assert scored["misses_at_5"] == ["direct-05"]
    by_id = {row["question_id"]: row for row in scored["questions"]}
    assert by_id["direct-01"]["metric_eligible"] is False
    assert by_id["direct-05"]["top_5"] is False
    assert by_id["paraphrased-05"]["top_1"] is True
    assert E5_MODEL_NAME == "intfloat/multilingual-e5-small"
