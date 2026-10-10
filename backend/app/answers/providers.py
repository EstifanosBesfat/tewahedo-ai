"""Answer providers that can cite only retrieved passages."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal, Protocol

from app.answers.citations import resolve_citations
from app.answers.schemas import (
    AnswerDraft,
    AnswerGenerationRequest,
    EvidenceAssessment,
    GeneratedAnswer,
    SourcePassage,
)

ABSTAIN_MISSING = {
    "am": "ከተገኙ ምንጮች ይህን ጥያቄ ማረጋገጥ አልተቻለም። የተመለሰ ምንጭ አልቀረበም።",
    "en": (
        "The available sources cannot establish an answer to this question. "
        "No source passage was retrieved."
    ),
}
ABSTAIN_CONTRADICTORY = {
    "am": (
        "ከተገኙ ምንጮች ይህን ጥያቄ ማረጋገጥ አልተቻለም። "
        "ያሉት ምንጮች አንድ ትምህርት ብቻ አያስረግጡም።"
    ),
    "en": (
        "The available sources cannot establish an answer to this question. "
        "The supplied passages do not establish one teaching."
    ),
}
ABSTAIN_MULTIPLE = {
    "am": (
        "ከተገኙ ምንጮች አንድ መልስ አልተመረጠም። ከአንድ በላይ ምንጭ ተመልሷል። "
        "ይህ መገምገሚያ ከምንጮቹ ውጭ ትምህርት አይጨምርም።"
    ),
    "en": (
        "No answer was selected from the retrieved sources. "
        "More than one passage was retrieved. "
        "This evaluation does not add teaching beyond those passages."
    ),
}
ABSTAIN_REJECTED = {
    "am": (
        "ከተገኙ ምንጮች ይህን ጥያቄ ማረጋገጥ አልተቻለም። "
        "የቀረበው ጥቅስ ከተመለሱት ምንጮች ጋር አይገጥምም።"
    ),
    "en": (
        "The available sources cannot establish an answer to this question. "
        "A proposed citation does not match a retrieved passage."
    ),
}
QUOTE_PREFIX = {
    "am": "የሚከተለው ቃል ከተመለሰው ምንጭ እንደተቀመጠ የተወሰደ ነው።",
    "en": "The following wording is copied from the retrieved source.",
}


class AnswerProvider(Protocol):
    """Generate an answer from a question and retrieved passages."""

    provider_name: str
    model_name: str | None

    def generate(self, request: AnswerGenerationRequest) -> GeneratedAnswer:
        """Return an answer, an abstention, and citations tied to passages."""


class ExtractiveAnswerProvider:
    """Quote one retrieved passage, or abstain when the evidence is not singular.

    This provider does not call a language model and does not add teaching
    beyond the stored passage text.
    """

    provider_name = "extractive-abstaining"
    model_name = None

    def generate(self, request: AnswerGenerationRequest) -> GeneratedAnswer:
        evidence = assess_evidence(
            request.passages,
            contradictory=request.contradictory,
            selected_parent_chunk_ids=request.selected_parent_chunk_ids,
        )
        if evidence.status == "single_passage":
            return self._quote(request, evidence)
        return self._abstain(request, evidence)

    def _quote(
        self,
        request: AnswerGenerationRequest,
        evidence: EvidenceAssessment,
    ) -> GeneratedAnswer:
        parent_id = evidence.selected_parent_chunk_id
        if parent_id is None:
            raise ValueError("a single-passage answer needs a selected parent")
        passage = _passage(request.passages, parent_id)
        citations, rejected = resolve_citations(
            [passage.parent_chunk_id],
            request.passages,
            "supports_answer",
        )
        if rejected or len(citations) != 1:
            raise ValueError("the selected passage could not be cited")
        return GeneratedAnswer(
            question_id=request.question_id,
            language=request.language,
            answer_text=f"{QUOTE_PREFIX[request.language]}\n\n{passage.text}",
            abstained=False,
            abstention_code="none",
            abstention_reason=None,
            citations=citations,
            supporting_parent_chunk_ids=[passage.parent_chunk_id],
            rejected_citation_ids=[],
            provider_name=self.provider_name,
            model_name=self.model_name,
        )

    def _abstain(
        self,
        request: AnswerGenerationRequest,
        evidence: EvidenceAssessment,
    ) -> GeneratedAnswer:
        code = _abstention_code(evidence.status)
        citations: list = []
        rejected: list[str] = []
        if evidence.status in {"contradictory", "multiple_passages"}:
            citations, rejected = resolve_citations(
                [passage.parent_chunk_id for passage in request.passages],
                request.passages,
                "unresolved_evidence",
            )
        elif evidence.status == "rejected_selection":
            rejected = [
                parent_id
                for parent_id in request.selected_parent_chunk_ids or []
                if parent_id not in {passage.parent_chunk_id for passage in request.passages}
            ]
        return GeneratedAnswer(
            question_id=request.question_id,
            language=request.language,
            answer_text=_abstain_text(code, request.language),
            abstained=True,
            abstention_code=code,
            abstention_reason=evidence.reason,
            citations=citations,
            supporting_parent_chunk_ids=[],
            rejected_citation_ids=rejected,
            provider_name=self.provider_name,
            model_name=self.model_name,
        )


class ConfiguredAnswerProvider:
    """Call an explicitly configured completion function.

    The function returns answer text and parent chunk ids. Document titles
    and page ranges are copied from the retrieved passages afterward.
    """

    provider_name = "configured"

    def __init__(
        self,
        model_name: str,
        complete: Callable[[AnswerGenerationRequest], AnswerDraft],
    ) -> None:
        cleaned = model_name.strip()
        if not cleaned:
            raise ValueError("model_name must be explicit")
        self.model_name = cleaned
        self._complete = complete

    def generate(self, request: AnswerGenerationRequest) -> GeneratedAnswer:
        draft = self._complete(request)
        citations, rejected = resolve_citations(
            draft.cited_parent_chunk_ids,
            request.passages,
            draft.citation_role,
            draft.excerpts_by_parent_chunk_id,
        )
        if rejected or (not draft.abstained and not citations):
            return GeneratedAnswer(
                question_id=request.question_id,
                language=request.language,
                answer_text=ABSTAIN_REJECTED[request.language],
                abstained=True,
                abstention_code="rejected_citations",
                abstention_reason=(
                    "A proposed citation did not match a retrieved passage."
                ),
                citations=[],
                supporting_parent_chunk_ids=[],
                rejected_citation_ids=rejected or list(draft.cited_parent_chunk_ids),
                discarded_answer_text=draft.answer_text,
                provider_name=self.provider_name,
                model_name=self.model_name,
            )
        supporting = [
            citation.parent_chunk_id
            for citation in citations
            if citation.role == "supports_answer" and not draft.abstained
        ]
        return GeneratedAnswer(
            question_id=request.question_id,
            language=request.language,
            answer_text=draft.answer_text,
            abstained=draft.abstained,
            abstention_code=draft.abstention_code,
            abstention_reason=None if not draft.abstained else draft.answer_text,
            citations=citations,
            supporting_parent_chunk_ids=supporting,
            rejected_citation_ids=[],
            provider_name=self.provider_name,
            model_name=self.model_name,
        )


def assess_evidence(
    passages: Sequence[SourcePassage],
    contradictory: bool = False,
    selected_parent_chunk_ids: Sequence[str] | None = None,
) -> EvidenceAssessment:
    """Decide whether the provider may quote a passage."""

    if not passages:
        return EvidenceAssessment(
            status="missing",
            reason="No retrieved source passage was supplied.",
            origin="passage_count",
        )
    retrieved = {passage.parent_chunk_id for passage in passages}
    selected = list(selected_parent_chunk_ids or [])
    if any(parent_id not in retrieved for parent_id in selected):
        return EvidenceAssessment(
            status="rejected_selection",
            reason="A selected parent chunk was not in the retrieved passages.",
            origin="selection",
        )
    if contradictory:
        return EvidenceAssessment(
            status="contradictory",
            reason=(
                "The evidence is marked as unable to establish one teaching "
                "from the available sources."
            ),
            origin="caller_flag",
        )
    if len(selected) > 1 or (not selected and len(passages) > 1):
        return EvidenceAssessment(
            status="multiple_passages",
            reason=(
                "More than one source passage is in scope. "
                "This provider does not choose among them or combine them "
                "into a new teaching."
            ),
            origin="selection" if selected else "passage_count",
        )
    parent_id = selected[0] if selected else passages[0].parent_chunk_id
    return EvidenceAssessment(
        status="single_passage",
        reason="One retrieved source passage is available to quote.",
        origin="selection" if selected else "passage_count",
        selected_parent_chunk_id=parent_id,
    )


def _passage(passages: Sequence[SourcePassage], parent_id: str) -> SourcePassage:
    for passage in passages:
        if passage.parent_chunk_id == parent_id:
            return passage
    raise ValueError(f"{parent_id} was not retrieved")


def _abstention_code(
    status: str,
) -> Literal[
    "missing_evidence",
    "contradictory_evidence",
    "multiple_passages",
    "rejected_citations",
]:
    if status == "missing":
        return "missing_evidence"
    if status == "contradictory":
        return "contradictory_evidence"
    if status == "rejected_selection":
        return "rejected_citations"
    return "multiple_passages"


def _abstain_text(code: str, language: str) -> str:
    if code == "missing_evidence":
        return ABSTAIN_MISSING[language]
    if code == "contradictory_evidence":
        return ABSTAIN_CONTRADICTORY[language]
    if code == "rejected_citations":
        return ABSTAIN_REJECTED[language]
    return ABSTAIN_MULTIPLE[language]
