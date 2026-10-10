"""Build parent passages from retrieval hits and the stored corpus."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from app.preparation.retrieval_units import parent_chunk_id
from app.retrieval.evaluation import collapse_units_to_parents
from app.retrieval.schemas import SearchResult
from app.answers.schemas import RetrievedUnitRef, SourcePassage


class ParentCorpus:
    """Read-only parent chunks. Text is kept exactly as stored."""

    def __init__(self, document: Mapping[str, object]) -> None:
        chunks = document.get("chunks")
        if not isinstance(chunks, list):
            raise ValueError("corpus must contain a chunks list")
        self.document_id = str(document["document_id"])
        self.source_filename = str(document["source_filename"])
        self._chunks: dict[str, Mapping[str, object]] = {}
        for chunk in chunks:
            if not isinstance(chunk, Mapping):
                raise ValueError("each corpus chunk must be an object")
            chunk_id = str(chunk["chunk_id"])
            text = chunk["text"]
            if not isinstance(text, str) or text == "":
                raise ValueError(f"{chunk_id} has no stored text")
            self._chunks[chunk_id] = chunk

    @classmethod
    def load(cls, path: Path) -> "ParentCorpus":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def text(self, parent_chunk_id_value: str) -> str:
        return str(self._chunk(parent_chunk_id_value)["text"])

    def passage(
        self,
        rank: int,
        parent_id: str,
        units: Sequence[RetrievedUnitRef],
    ) -> SourcePassage:
        chunk = self._chunk(parent_id)
        return SourcePassage(
            rank=rank,
            document_id=str(chunk["document_id"]),
            source_filename=self.source_filename,
            parent_chunk_id=str(chunk["chunk_id"]),
            page_start=int(chunk["page_start"]),
            page_end=int(chunk["page_end"]),
            extraction_method=str(chunk["extraction_method"]),
            source_quality_score=float(chunk["source_quality_score"]),
            text=str(chunk["text"]),
            retrieved_units=list(units),
        )

    def _chunk(self, parent_id: str) -> Mapping[str, object]:
        try:
            return self._chunks[parent_id]
        except KeyError as exc:
            raise ValueError(f"retrieved parent {parent_id} is not in the corpus") from exc


def passages_from_search_results(
    hits: Sequence[SearchResult],
    corpus: ParentCorpus,
    width: int = 5,
) -> list[SourcePassage]:
    """Collapse unit hits to parents and attach the stored parent text."""

    if width < 1:
        raise ValueError("width must be at least 1")
    parent_ids = collapse_units_to_parents(
        [hit.chunk_id for hit in hits],
        width=width,
    )
    return _passages_for_parents(parent_ids, _units_from_hits(hits), corpus)


def passages_from_frozen_ranking(
    question: Mapping[str, object],
    corpus: ParentCorpus,
    width: int = 5,
) -> list[SourcePassage]:
    """Rebuild passages from a frozen ranking without searching again."""

    unit_ranking = question.get("unit_ranking")
    parent_ranking = question.get("parent_ranking")
    if not isinstance(unit_ranking, list) or not isinstance(parent_ranking, list):
        raise ValueError("frozen ranking is missing unit or parent rows")
    unit_ids = [str(row["unit_id"]) for row in unit_ranking if isinstance(row, Mapping)]
    collapsed = collapse_units_to_parents(unit_ids, width=width)
    stored = [
        str(row["parent_chunk_id"])
        for row in parent_ranking
        if isinstance(row, Mapping)
    ]
    if collapsed != stored:
        raise ValueError("frozen parent ranking does not match the unit collapse")
    units: dict[str, list[RetrievedUnitRef]] = {}
    for row in unit_ranking:
        if not isinstance(row, Mapping):
            continue
        parent_id = str(row["parent_chunk_id"])
        if parent_chunk_id(str(row["unit_id"])) != parent_id:
            raise ValueError("frozen unit parent does not match its unit id")
        units.setdefault(parent_id, []).append(
            RetrievedUnitRef(
                rank=int(row["rank"]),
                unit_id=str(row["unit_id"]),
                page_start=int(row["page_start"]),
                page_end=int(row["page_end"]),
                similarity_score=float(row["similarity_score"]),
            )
        )
    return _passages_for_parents(stored, units, corpus)


def _units_from_hits(
    hits: Sequence[SearchResult],
) -> dict[str, list[RetrievedUnitRef]]:
    units: dict[str, list[RetrievedUnitRef]] = {}
    for rank, hit in enumerate(hits, start=1):
        parent_id = parent_chunk_id(hit.chunk_id)
        units.setdefault(parent_id, []).append(
            RetrievedUnitRef(
                rank=rank,
                unit_id=hit.chunk_id,
                page_start=hit.page_start,
                page_end=hit.page_end,
                similarity_score=hit.similarity_score,
            )
        )
    return units


def _passages_for_parents(
    parent_ids: Sequence[str],
    units: Mapping[str, Sequence[RetrievedUnitRef]],
    corpus: ParentCorpus,
) -> list[SourcePassage]:
    return [
        corpus.passage(rank, parent_id, units.get(parent_id, []))
        for rank, parent_id in enumerate(parent_ids, start=1)
    ]
