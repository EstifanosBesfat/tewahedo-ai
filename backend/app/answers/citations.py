"""Attach citations from retrieved passage metadata and check them."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

from app.answers.schemas import (
    AutomaticChecks,
    Citation,
    EvidenceAssessment,
    GeneratedAnswer,
    SourcePassage,
)


def resolve_citations(
    parent_ids: Sequence[str],
    passages: Sequence[SourcePassage],
    role: Literal["supports_answer", "unresolved_evidence"],
    excerpts: Mapping[str, str] | None = None,
) -> tuple[list[Citation], list[str]]:
    """Copy document, page, and excerpt data from retrieved passages.

    Parent ids that were not retrieved, and excerpts that are not exact
    substrings of the stored passage, are returned as rejected ids.
    """

    by_id = {passage.parent_chunk_id: passage for passage in passages}
    citations: list[Citation] = []
    rejected: list[str] = []
    for parent_id in parent_ids:
        passage = by_id.get(parent_id)
        if passage is None:
            rejected.append(parent_id)
            continue
        excerpt = passage.text if excerpts is None else excerpts.get(parent_id, "")
        if excerpt == "" or excerpt not in passage.text:
            rejected.append(parent_id)
            continue
        citations.append(
            Citation(
                document_id=passage.document_id,
                source_filename=passage.source_filename,
                parent_chunk_id=passage.parent_chunk_id,
                page_start=passage.page_start,
                page_end=passage.page_end,
                excerpt=excerpt,
                role=role,
            )
        )
    return citations, rejected


def automatic_checks(
    answer: GeneratedAnswer,
    passages: Sequence[SourcePassage],
    evidence: EvidenceAssessment,
    corpus_texts: Mapping[str, str] | None = None,
) -> AutomaticChecks:
    """Check citation identity. This does not judge theological truth."""

    by_id = {passage.parent_chunk_id: passage for passage in passages}
    unmatched: list[str] = []
    excerpts_ok = True
    pages_ok = True
    documents_ok = True
    for citation in answer.citations:
        passage = by_id.get(citation.parent_chunk_id)
        if passage is None:
            unmatched.append(citation.parent_chunk_id)
            excerpts_ok = False
            pages_ok = False
            documents_ok = False
            continue
        if (
            citation.document_id != passage.document_id
            or citation.source_filename != passage.source_filename
        ):
            documents_ok = False
            unmatched.append(citation.parent_chunk_id)
        if (
            citation.page_start != passage.page_start
            or citation.page_end != passage.page_end
        ):
            pages_ok = False
            unmatched.append(citation.parent_chunk_id)
        if citation.excerpt not in passage.text:
            excerpts_ok = False
            unmatched.append(citation.parent_chunk_id)
    unmatched.extend(answer.rejected_citation_ids)
    joined = "\n".join(passage.text for passage in passages)
    separated = answer.answer_text != joined and all(
        answer.answer_text != passage.text for passage in passages
    )
    corpus_ok = True
    if corpus_texts is not None:
        corpus_ok = all(
            corpus_texts.get(passage.parent_chunk_id) == passage.text
            for passage in passages
        )
    unique_unmatched = list(dict.fromkeys(unmatched))
    return AutomaticChecks(
        citation_count=len(answer.citations),
        citations_match_retrieved_passages=(
            not unique_unmatched and excerpts_ok and pages_ok and documents_ok
        ),
        unmatched_citations=unique_unmatched,
        excerpts_are_exact_substrings=excerpts_ok,
        page_ranges_match_parent_records=pages_ok,
        document_ids_match_parent_records=documents_ok,
        answer_text_differs_from_each_source_passage=separated,
        source_passages_match_corpus=corpus_ok,
        abstained=answer.abstained,
        evidence_status=evidence.status,
    )
