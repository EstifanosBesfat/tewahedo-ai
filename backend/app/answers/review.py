"""Human review of retrieved passages, separate from retrieval metrics."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.answers.dataset import FROZEN_EVALUATION_FILES, assert_writable_output
from app.answers.passages import ParentCorpus
from app.answers.schemas import AnswerEvaluationDataset

PROTECTED_REVIEW_SOURCES = FROZEN_EVALUATION_FILES | {
    "answer-evaluation-bge-m3.json",
    "answer-evaluation-bge-m3-report.md",
}

REVIEW_DESCRIPTION = (
    "Human review of the frozen BGE-M3 answer evaluation. "
    "A person records whether the retrieved passages establish an answer. "
    "Retrieval-metric eligibility stays on its own field, and no model "
    "approves the proposed answer."
)


class ReviewValidationError(ValueError):
    """A review names evidence that was not retrieved for that question."""


class ReviewPassage(BaseModel):
    """One retrieved parent shown to the reviewer."""

    rank: int = Field(ge=1)
    parent_chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    source_filename: str = Field(min_length=1)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_page_range(self) -> "ReviewPassage":
        if self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        return self


class ReviewWorksheetQuestion(BaseModel):
    """Read-only context for one question."""

    question_id: str
    question: str = Field(min_length=1)
    category: Literal["direct", "paraphrased", "conceptual"]
    expected_concept: str | None
    retrieval_metric_eligible: bool
    retrieval_exclusion_reason: str | None = None
    automatic_abstention_code: str
    passages: list[ReviewPassage]


class ReviewSubmission(BaseModel):
    """Fields a person may fill. Pages and document titles are not accepted."""

    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1)
    status: Literal["pending", "reviewed"] = "pending"
    answerable: Literal["yes", "no", "ambiguous"] | None = None
    selected_parent_chunk_ids: list[str] = Field(default_factory=list)
    qualifications_or_contradictions: str = ""
    proposed_answer: str = ""
    proposed_answer_has_unsupported_part: bool | None = None
    reviewer_notes: str = ""
    reviewer: str | None = None

    @model_validator(mode="after")
    def validate_review_state(self) -> "ReviewSubmission":
        completed = (
            self.answerable is not None
            or self.selected_parent_chunk_ids
            or self.qualifications_or_contradictions.strip()
            or self.proposed_answer.strip()
            or self.proposed_answer_has_unsupported_part is not None
            or (self.reviewer is not None and self.reviewer.strip() != "")
            or self.reviewer_notes.strip()
        )
        if self.status == "pending" and completed:
            raise ValueError("a pending review cannot contain review judgments")
        if self.status == "reviewed":
            if self.answerable is None:
                raise ValueError("a completed review needs answerable set to yes, no, or ambiguous")
            if self.proposed_answer_has_unsupported_part is None:
                raise ValueError("a completed review must say whether the proposed answer has an unsupported part")
            if self.reviewer is None or not self.reviewer.strip():
                raise ValueError("a completed review needs a reviewer name")
            if not self.proposed_answer.strip():
                raise ValueError("a completed review needs the reviewer's proposed answer")
            if self.answerable == "yes" and not self.selected_parent_chunk_ids:
                raise ValueError("an answerable yes review must select at least one retrieved parent")
            if self.answerable == "ambiguous" and not self.qualifications_or_contradictions.strip():
                raise ValueError("an ambiguous review must record the qualification or contradiction")
            if self.answerable == "ambiguous" and not self.selected_parent_chunk_ids:
                raise ValueError("an ambiguous review must select the retrieved parents involved")
        return self


class SelectedEvidence(BaseModel):
    """Passage metadata copied from the retrieved parent, not from the reviewer."""

    rank: int = Field(ge=1)
    parent_chunk_id: str
    document_id: str
    source_filename: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    text: str = Field(min_length=1)
    role: Literal["supports_answer", "unresolved_evidence", "examined_not_sufficient"]


class ReviewedQuestion(BaseModel):
    question_id: str
    question: str
    category: Literal["direct", "paraphrased", "conceptual"]
    expected_concept: str | None
    retrieval_metric_eligible: bool
    retrieval_exclusion_reason: str | None = None
    automatic_abstention_code: str
    retrieved_passages: list[ReviewPassage]
    status: Literal["pending", "reviewed"]
    answerable: Literal["yes", "no", "ambiguous"] | None = None
    qualifications_or_contradictions: str = ""
    proposed_answer: str = ""
    proposed_answer_has_unsupported_part: bool | None = None
    reviewer_notes: str = ""
    reviewer: str | None = None
    evidence_label: Literal[
        "pending",
        "missing",
        "contradictory",
        "selected",
        "examined_not_sufficient",
    ]
    selected_evidence: list[SelectedEvidence]


class AnswerReviewDataset(BaseModel):
    schema_version: Literal["1"]
    description: str = Field(min_length=1)
    source_answer_evaluation: str
    source_answer_evaluation_sha256: str
    ground_truth_file: str
    corpus_file: str
    question_count: int = Field(ge=0)
    records: list[ReviewedQuestion]

    @model_validator(mode="after")
    def validate_count(self) -> "AnswerReviewDataset":
        if self.question_count != len(self.records):
            raise ValueError("question_count must match the number of records")
        return self


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"]
    reviews: list[ReviewSubmission]


def load_expected_concepts(path: Path) -> dict[str, str | None]:
    """Read expected concepts without writing the ground-truth file."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("ground truth must contain questions")
    concepts: dict[str, str | None] = {}
    questions_by_id: dict[str, str] = {}
    for question in questions:
        if not isinstance(question, Mapping) or "expected_concept" not in question:
            raise ValueError("each ground-truth question needs expected_concept")
        question_id = str(question["question_id"])
        concept = question["expected_concept"]
        if concept is not None and not isinstance(concept, str):
            raise ValueError(f"{question_id} expected_concept must be text or null")
        concepts[question_id] = concept
        questions_by_id[question_id] = str(question["question"])
    return concepts


def load_ground_truth_questions(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("ground truth must contain questions")
    return {
        str(question["question_id"]): str(question["question"])
        for question in questions
        if isinstance(question, Mapping)
    }


def build_review_worksheet(
    dataset: AnswerEvaluationDataset,
    expected_concepts: Mapping[str, str | None],
    ground_truth_questions: Mapping[str, str],
    corpus: ParentCorpus,
) -> list[ReviewWorksheetQuestion]:
    """Copy retrieved parents into a reviewer worksheet."""

    dataset_ids = {record.question_id for record in dataset.records}
    if dataset_ids != set(expected_concepts) or dataset_ids != set(ground_truth_questions):
        raise ValueError("answer evaluation questions must match the ground-truth ids")
    worksheet: list[ReviewWorksheetQuestion] = []
    for record in dataset.records:
        if ground_truth_questions[record.question_id] != record.question:
            raise ValueError(f"{record.question_id} question text does not match ground truth")
        passages = [_passage_from_record(passage, corpus) for passage in record.source_passages_retrieved]
        ranking_ids = [parent.parent_chunk_id for parent in record.retrieved_parent_ranking]
        if [passage.parent_chunk_id for passage in passages] != ranking_ids:
            raise ValueError(f"{record.question_id} parent ranking does not match its passages")
        worksheet.append(
            ReviewWorksheetQuestion(
                question_id=record.question_id,
                question=record.question,
                category=record.category,
                expected_concept=expected_concepts[record.question_id],
                retrieval_metric_eligible=record.retrieval_metric_eligible,
                retrieval_exclusion_reason=record.retrieval_exclusion_reason,
                automatic_abstention_code=record.generated_answer.abstention_code,
                passages=passages,
            )
        )
    return worksheet


def pending_submissions(
    worksheet: Sequence[ReviewWorksheetQuestion],
) -> list[ReviewSubmission]:
    return [
        ReviewSubmission(question_id=question.question_id, status="pending")
        for question in worksheet
    ]


def apply_answer_reviews(
    worksheet: Sequence[ReviewWorksheetQuestion],
    submissions: Sequence[ReviewSubmission],
    source_name: str,
    source_sha256: str,
    ground_truth_file: str,
    corpus_file: str,
) -> AnswerReviewDataset:
    """Validate selections and copy source metadata onto the reviewed dataset."""

    by_id = {submission.question_id: submission for submission in submissions}
    if len(by_id) != len(submissions):
        raise ReviewValidationError("each question can have only one review")
    worksheet_ids = [question.question_id for question in worksheet]
    if set(by_id) != set(worksheet_ids):
        raise ReviewValidationError("reviews must cover the worksheet questions exactly")
    records = [
        _apply_one(question, by_id[question.question_id])
        for question in worksheet
    ]
    return AnswerReviewDataset(
        schema_version="1",
        description=REVIEW_DESCRIPTION,
        source_answer_evaluation=source_name,
        source_answer_evaluation_sha256=source_sha256,
        ground_truth_file=ground_truth_file,
        corpus_file=corpus_file,
        question_count=len(records),
        records=records,
    )


def render_review_packet(worksheet: Sequence[ReviewWorksheetQuestion]) -> str:
    """Markdown view a person can read while filling the review input."""

    lines = [
        "# Answer review packet",
        "",
        "Each section shows the original question, the ground-truth expected concept, and the top retrieved parent chunks. Record decisions in the review input. Answerability is separate from retrieval-metric eligibility.",
        "",
        "Fill `answerable` with `yes`, `no`, or `ambiguous`. Select parent chunk IDs only from the list in that section. Leave document IDs and page numbers out of the review input; the validator copies them from the retrieved passage.",
        "",
    ]
    for question in worksheet:
        concept = question.expected_concept if question.expected_concept else "none recorded"
        eligibility = "yes" if question.retrieval_metric_eligible else "no"
        lines.extend(
            [
                f"## {question.question_id}",
                "",
                f"Question: {question.question}",
                "",
                f"Expected concept: {concept}",
                "",
                f"Retrieval metric eligible: {eligibility}",
            ]
        )
        if question.retrieval_exclusion_reason:
            lines.append(f"Retrieval exclusion: {question.retrieval_exclusion_reason}")
        lines.extend(
            [
                "",
                f"Automatic answer check: abstained (`{question.automatic_abstention_code}`). This is not a human judgment.",
                "",
            ]
        )
        if not question.passages:
            lines.append("Retrieved parents: none.")
            lines.append("")
        for passage in question.passages:
            lines.extend(
                [
                    f"### Rank {passage.rank}",
                    "",
                    f"- Parent chunk: `{passage.parent_chunk_id}`",
                    f"- Document: `{passage.document_id}`",
                    f"- Source file: `{passage.source_filename}`",
                    f"- Pages: {passage.page_start}–{passage.page_end}",
                    "",
                    _fence(passage.text),
                    "",
                ]
            )
    return "\n".join(lines)


def render_review_report(dataset: AnswerReviewDataset) -> str:
    """Summarize completed reviews separately from pending cases."""

    records = dataset.records
    reviewed = [record for record in records if record.status == "reviewed"]
    pending = [record for record in records if record.status == "pending"]
    lines = [
        "# Human review of source-grounded answers",
        "",
        dataset.description,
        "",
        f"- Source answer evaluation: `{_display_path(dataset.source_answer_evaluation)}`",
        f"- Source sha256: `{dataset.source_answer_evaluation_sha256}`",
        f"- Questions: {dataset.question_count}",
        f"- Completed reviews: {len(reviewed)}",
        f"- Pending cases: {len(pending)}",
        "",
        "## Answerability",
        "",
        "These counts include completed reviews only.",
        "",
        "| Answerable from available sources | Count |",
        "| --- | ---: |",
        f"| yes | {_answerable(reviewed, 'yes')} |",
        f"| no | {_answerable(reviewed, 'no')} |",
        f"| ambiguous | {_answerable(reviewed, 'ambiguous')} |",
        "",
        "## Selected evidence",
        "",
        "| Evidence label | Count |",
        "| --- | ---: |",
        f"| missing | {_label(reviewed, 'missing')} |",
        f"| contradictory | {_label(reviewed, 'contradictory')} |",
        f"| selected supporting passages | {_label(reviewed, 'selected')} |",
        f"| examined but not sufficient | {_label(reviewed, 'examined_not_sufficient')} |",
        f"| proposed answers with an unsupported part | {_unsupported(reviewed)} |",
        "",
        "## Retrieval eligibility",
        "",
        "Retrieval-metric eligibility is copied from the frozen answer evaluation. It is not changed by a reviewer's answerability decision.",
        "",
        f"- Metric-eligible questions: {sum(record.retrieval_metric_eligible for record in records)}",
        f"- Excluded from retrieval metrics: {sum(not record.retrieval_metric_eligible for record in records)}",
        "",
        "## Completed reviews",
        "",
    ]
    if reviewed:
        lines.extend(
            [
                "| Question | Answerable | Selected parents | Unsupported part | Evidence |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for record in reviewed:
            selected = ", ".join(
                evidence.parent_chunk_id for evidence in record.selected_evidence
            ) or "none"
            lines.append(
                f"| {record.question_id} | {record.answerable} | {selected} | "
                f"{record.proposed_answer_has_unsupported_part} | {record.evidence_label} |"
            )
    else:
        lines.append("No reviews are completed.")
    lines.extend(["", "## Pending cases", ""])
    if pending:
        for record in pending:
            lines.append(
                f"- `{record.question_id}`: retrieval metric eligible "
                f"{'yes' if record.retrieval_metric_eligible else 'no'}; answerability pending"
            )
    else:
        lines.append("No cases are pending.")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- Selected chunk IDs are accepted only when they appear in that question's retrieved parents.",
            "- Document IDs and page ranges are copied from those parent records.",
            "- Source text stays in the passage field, and the proposed answer stays in its own field.",
            "- The starting answer-evaluation dataset is read and not replaced by this review file.",
            "",
        ]
    )
    return "\n".join(lines)


def assert_review_output(path: Path) -> None:
    assert_writable_output(path)
    if path.name in PROTECTED_REVIEW_SOURCES:
        raise ValueError(f"{path.name} is a frozen evaluation artifact")


def write_review_outputs(
    packet: str,
    review_input: ReviewInput,
    dataset: AnswerReviewDataset,
    packet_path: Path,
    input_path: Path,
    dataset_path: Path,
    report_path: Path,
    write_input: bool,
) -> None:
    for path in (packet_path, input_path, dataset_path, report_path):
        assert_review_output(path)
    _write_text(packet_path, packet)
    if write_input:
        _write_text(
            input_path,
            json.dumps(review_input.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        )
    _write_text(
        dataset_path,
        json.dumps(dataset.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    _write_text(report_path, render_review_report(dataset))


def load_review_input(path: Path) -> ReviewInput:
    try:
        return ReviewInput.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        raise ReviewValidationError("review input failed validation") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _passage_from_record(passage: object, corpus: ParentCorpus) -> ReviewPassage:
    parent_id = str(getattr(passage, "parent_chunk_id"))
    stored = corpus.record(parent_id)
    text = str(stored["text"])
    document_id = str(stored["document_id"])
    page_start = int(stored["page_start"])
    page_end = int(stored["page_end"])
    if (
        text != getattr(passage, "text")
        or document_id != getattr(passage, "document_id")
        or page_start != getattr(passage, "page_start")
        or page_end != getattr(passage, "page_end")
        or corpus.source_filename != getattr(passage, "source_filename")
    ):
        raise ReviewValidationError(
            f"{parent_id} does not match the stored corpus record"
        )
    return ReviewPassage(
        rank=int(getattr(passage, "rank")),
        parent_chunk_id=parent_id,
        document_id=document_id,
        source_filename=corpus.source_filename,
        page_start=page_start,
        page_end=page_end,
        text=text,
    )


def _apply_one(
    question: ReviewWorksheetQuestion,
    submission: ReviewSubmission,
) -> ReviewedQuestion:
    if submission.question_id != question.question_id:
        raise ReviewValidationError("review question id does not match the worksheet")
    retrieved = {passage.parent_chunk_id: passage for passage in question.passages}
    seen: set[str] = set()
    for parent_id in submission.selected_parent_chunk_ids:
        if parent_id not in retrieved:
            raise ReviewValidationError(
                f"{question.question_id} selected {parent_id}, which was not retrieved"
            )
        if parent_id in seen:
            raise ReviewValidationError(
                f"{question.question_id} repeats selected parent {parent_id}"
            )
        seen.add(parent_id)
    for passage in question.passages:
        if submission.proposed_answer == passage.text:
            raise ReviewValidationError(
                "the proposed answer must stay separate from the source passage"
            )
    evidence_label, role = _evidence_label(submission)
    selected: list[SelectedEvidence] = []
    if role is not None:
        selected = [
            SelectedEvidence(
                rank=retrieved[parent_id].rank,
                parent_chunk_id=retrieved[parent_id].parent_chunk_id,
                document_id=retrieved[parent_id].document_id,
                source_filename=retrieved[parent_id].source_filename,
                page_start=retrieved[parent_id].page_start,
                page_end=retrieved[parent_id].page_end,
                text=retrieved[parent_id].text,
                role=role,
            )
            for parent_id in submission.selected_parent_chunk_ids
        ]
    return ReviewedQuestion(
        question_id=question.question_id,
        question=question.question,
        category=question.category,
        expected_concept=question.expected_concept,
        retrieval_metric_eligible=question.retrieval_metric_eligible,
        retrieval_exclusion_reason=question.retrieval_exclusion_reason,
        automatic_abstention_code=question.automatic_abstention_code,
        retrieved_passages=list(question.passages),
        status=submission.status,
        answerable=submission.answerable,
        qualifications_or_contradictions=submission.qualifications_or_contradictions,
        proposed_answer=submission.proposed_answer,
        proposed_answer_has_unsupported_part=submission.proposed_answer_has_unsupported_part,
        reviewer_notes=submission.reviewer_notes,
        reviewer=submission.reviewer,
        evidence_label=evidence_label,
        selected_evidence=selected,
    )


def _evidence_label(
    submission: ReviewSubmission,
) -> tuple[
    Literal["pending", "missing", "contradictory", "selected", "examined_not_sufficient"],
    Literal["supports_answer", "unresolved_evidence", "examined_not_sufficient"] | None,
]:
    if submission.status == "pending":
        return "pending", None
    if submission.answerable == "ambiguous":
        return "contradictory", "unresolved_evidence"
    if submission.answerable == "yes":
        return "selected", "supports_answer"
    if submission.selected_parent_chunk_ids:
        return "examined_not_sufficient", "examined_not_sufficient"
    return "missing", None


def _fence(text: str) -> str:
    marker = "```"
    while marker in text:
        marker += "`"
    return f"{marker}text\n{text}\n{marker}"


def _answerable(records: Sequence[ReviewedQuestion], value: str) -> int:
    return sum(record.answerable == value for record in records)


def _label(records: Sequence[ReviewedQuestion], value: str) -> int:
    return sum(record.evidence_label == value for record in records)


def _unsupported(records: Sequence[ReviewedQuestion]) -> int:
    return sum(record.proposed_answer_has_unsupported_part is True for record in records)


def _display_path(path: str) -> str:
    marker = "backend/"
    normalized = path.replace("\\", "/")
    index = normalized.rfind(marker)
    if index == -1:
        return path
    return normalized[index:]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)
