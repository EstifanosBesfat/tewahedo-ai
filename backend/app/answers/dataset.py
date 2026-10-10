"""Build an answer-evaluation dataset without changing retrieval artifacts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from app.answers.citations import automatic_checks
from app.answers.passages import ParentCorpus, passages_from_frozen_ranking
from app.answers.providers import ExtractiveAnswerProvider, assess_evidence
from app.answers.schemas import (
    AnswerEvaluationDataset,
    AnswerEvaluationRecord,
    AnswerGenerationRequest,
    EvidenceAssessment,
    GeneratedAnswer,
    HumanAnswerReview,
    RankedParent,
    SourcePassage,
)

FROZEN_EVALUATION_FILES = frozenset(
    {
        "amharic_retrieval_questions.json",
        "ground-truth-v2.json",
        "ground-truth-v2-proposal.json",
        "ground-truth-v3.json",
        "ground-truth-validation.json",
        "ground-truth-validation-report.md",
        "multilingual-e5-small.results.json",
        "retrieval-audit.json",
        "retrieval-evaluation-bge-m3.json",
        "retrieval-evaluation-bge-m3-report.md",
        "retrieval-evaluation-bge-m3-resources.json",
        "retrieval-evaluation-v2.json",
        "retrieval-evaluation-v2-report.md",
        "retrieval-evaluation-v3.json",
        "retrieval-evaluation-v3-report.md",
        "retrieval-miss-diagnostic.json",
        "retrieval-miss-diagnostic.md",
        "retrieval-unit-comparison.json",
    }
)

DATASET_DESCRIPTION = (
    "Source-grounded answer evaluation for the frozen BAAI/bge-m3 dense "
    "retrieval run. Answers are produced by an extractive provider that "
    "quotes one retrieved parent passage or abstains. Human factual-support "
    "judgments are pending and are stored separately from automatic checks."
)


def assert_writable_output(path: Path) -> None:
    if path.name in FROZEN_EVALUATION_FILES:
        raise ValueError(f"{path.name} is a frozen evaluation artifact")


def build_answer_dataset(
    questions_path: Path,
    retrieval_path: Path,
    corpus_path: Path,
    provider: ExtractiveAnswerProvider | None = None,
) -> AnswerEvaluationDataset:
    """Join the question file, frozen BGE-M3 rankings, and parent chunks."""

    answer_provider = provider or ExtractiveAnswerProvider()
    questions = _read_json(questions_path)
    retrieval = _read_json(retrieval_path)
    if retrieval.get("model_name") != "BAAI/bge-m3":
        raise ValueError("answer evaluation expects the frozen BGE-M3 results")
    corpus = ParentCorpus.load(corpus_path)
    question_rows = questions.get("questions")
    retrieval_rows = retrieval.get("questions")
    if not isinstance(question_rows, list) or not isinstance(retrieval_rows, list):
        raise ValueError("question and retrieval files must contain questions")
    retrieval_by_id = {
        str(row["question_id"]): row
        for row in retrieval_rows
        if isinstance(row, Mapping)
    }
    records: list[AnswerEvaluationRecord] = []
    for item in question_rows:
        if not isinstance(item, Mapping):
            raise ValueError("each evaluation question must be an object")
        question_id = str(item["question_id"])
        ranked = retrieval_by_id.get(question_id)
        if ranked is None:
            raise ValueError(f"{question_id} has no frozen retrieval row")
        if str(ranked["question"]) != str(item["question"]):
            raise ValueError(f"{question_id} question text does not match retrieval")
        passages = passages_from_frozen_ranking(ranked, corpus)
        contradictory = not bool(ranked["metric_eligible"])
        request = AnswerGenerationRequest(
            question_id=question_id,
            question=str(item["question"]),
            language="am",
            passages=passages,
            contradictory=contradictory,
        )
        answer = answer_provider.generate(request)
        evidence = assess_evidence(
            passages,
            contradictory=contradictory,
        )
        records.append(
            _record(
                question_id=question_id,
                question=str(item["question"]),
                category=str(item["category"]),
                metric_eligible=bool(ranked["metric_eligible"]),
                exclusion_reason=_optional_text(ranked.get("exclusion_reason")),
                passages=passages,
                answer=answer,
                evidence=evidence,
                corpus=corpus,
            )
        )
    return AnswerEvaluationDataset(
        schema_version="1",
        description=DATASET_DESCRIPTION,
        retrieval_model="BAAI/bge-m3",
        answer_provider=answer_provider.provider_name,
        answer_model=answer_provider.model_name,
        question_file=questions_path.as_posix(),
        retrieval_results_file=retrieval_path.as_posix(),
        corpus_file=corpus_path.as_posix(),
        question_count=len(records),
        frozen_input_sha256={
            "questions": _sha256(questions_path),
            "retrieval_results": _sha256(retrieval_path),
            "corpus": _sha256(corpus_path),
        },
        records=records,
    )


def render_answer_report(dataset: AnswerEvaluationDataset) -> str:
    """Separate automatic citation checks from pending human judgments."""

    records = dataset.records
    reviewed = [record for record in records if record.human_review.status == "reviewed"]
    pending = [record for record in records if record.human_review.status == "pending"]
    citation_matches = _count(
        records,
        lambda record: record.automatic_checks.citations_match_retrieved_passages,
    )
    exact_excerpts = _count(
        records,
        lambda record: record.automatic_checks.excerpts_are_exact_substrings,
    )
    corpus_matches = _count(
        records,
        lambda record: record.automatic_checks.source_passages_match_corpus,
    )
    separated = _count(
        records,
        lambda record: record.automatic_checks.answer_text_differs_from_each_source_passage,
    )
    abstentions = _count(records, lambda record: record.generated_answer.abstained)
    evidence_counts = {
        status: _count(records, lambda record, status=status: record.evidence.status == status)
        for status in (
            "missing",
            "contradictory",
            "multiple_passages",
            "rejected_selection",
            "single_passage",
        )
    }
    automatic_failures = [
        record.question_id
        for record in records
        if not record.automatic_checks.citations_match_retrieved_passages
        or not record.automatic_checks.source_passages_match_corpus
        or not record.automatic_checks.answer_text_differs_from_each_source_passage
    ]
    lines = [
        "# Source-grounded answer evaluation",
        "",
        dataset.description,
        "",
        "## Scope",
        "",
        f"- Retrieval model: `{dataset.retrieval_model}`",
        f"- Answer provider: `{dataset.answer_provider}`",
        f"- Answer model: `{dataset.answer_model or 'none'}`",
        f"- Questions evaluated: {dataset.question_count}",
        f"- Question file: `{_display_path(dataset.question_file)}`",
        f"- Retrieval results: `{_display_path(dataset.retrieval_results_file)}`",
        f"- Parent corpus: `{_display_path(dataset.corpus_file)}`",
        "",
        "## Automatic checks",
        "",
        "These checks confirm provenance. Teaching support is recorded only under human judgments.",
        "",
        "| Check | Count |",
        "| --- | ---: |",
        f"| Questions evaluated | {dataset.question_count} |",
        f"| Citation sets matching retrieved chunks | {citation_matches} |",
        f"| Excerpts that are exact substrings | {exact_excerpts} |",
        f"| Source passages identical to the stored corpus | {corpus_matches} |",
        f"| Answer texts stored separately from source passages | {separated} |",
        f"| Abstentions | {abstentions} |",
        f"| Missing evidence | {evidence_counts['missing']} |",
        f"| Contradictory or non-establishing evidence | {evidence_counts['contradictory']} |",
        f"| Multiple passages left unresolved | {evidence_counts['multiple_passages']} |",
        f"| Rejected citation selections | {evidence_counts['rejected_selection']} |",
        f"| Single-passage quotations | {evidence_counts['single_passage']} |",
        f"| Automatic provenance failures | {len(automatic_failures)} |",
        "",
        "## Human judgments",
        "",
        "A row counts in this section only when `human_review.status` is `reviewed`.",
        "",
        "| Judgment | Count |",
        "| --- | ---: |",
        f"| Reviewed records | {len(reviewed)} |",
        f"| Answers marked supported by sources | {_human(reviewed, 'factual_support', 'supported')} |",
        f"| Answers marked partially supported | {_human(reviewed, 'factual_support', 'partially_supported')} |",
        f"| Answers marked unsupported | {_human(reviewed, 'factual_support', 'unsupported')} |",
        f"| Important qualifications omitted | {_human_true(reviewed, 'important_qualifications_omitted')} |",
        f"| Unsupported claims present | {_human_true(reviewed, 'contains_unsupported_claims')} |",
        f"| Abstentions marked appropriate | {_appropriate_abstentions(reviewed)} |",
        f"| Records awaiting human review | {len(pending)} |",
        "",
        "## Questions",
        "",
        "| Question | Evidence | Abstained | Citations match | Human review |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| {question_id} | {status} | {abstained} | {match} | {review} |".format(
                question_id=record.question_id,
                status=record.evidence.status,
                abstained=record.generated_answer.abstention_code,
                match=record.automatic_checks.citations_match_retrieved_passages,
                review=record.human_review.status,
            )
        )
    lines.extend(
        [
            "",
            "## Failures awaiting human review",
            "",
        ]
    )
    if pending:
        lines.append(
            "Every pending record still needs a person to judge answerability, "
            "factual support, omitted qualifications, and unsupported claims."
        )
        lines.append("")
        for record in pending:
            lines.append(
                f"- `{record.question_id}`: {record.evidence.reason}"
            )
    else:
        lines.append("No records are awaiting human review.")
    if automatic_failures:
        lines.extend(["", "Automatic provenance failures:", ""])
        for question_id in automatic_failures:
            lines.append(f"- `{question_id}`")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The extractive provider quotes a passage only when exactly one retrieved parent is in scope.",
            "- The frozen top-five parent lists contain more than one passage, so those questions abstain.",
            "- `direct-01` abstains because the frozen BGE-M3 result marks it metric-ineligible.",
            "- Citation pages and document ids are copied from parent chunk records.",
            "- No language-model provider or API key is configured for this run.",
            "- Automatic checks do not accept a model's self-evaluation as factual support.",
            "- OCR text, retrieval units, embeddings, ranking, and the retrieval benchmark files stay unchanged.",
            "",
            "## Next step",
            "",
            "A reviewer can mark each pending record, or name one supporting parent chunk for a later extractive quotation. A language model can be attached only through `ConfiguredAnswerProvider` with an explicit model name; its citations still have to match retrieved chunks before human review.",
            "",
        ]
    )
    return "\n".join(lines)


def write_answer_outputs(
    dataset: AnswerEvaluationDataset,
    json_path: Path,
    report_path: Path,
) -> None:
    assert_writable_output(json_path)
    assert_writable_output(report_path)
    _write_text(
        json_path,
        json.dumps(dataset.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    _write_text(report_path, render_answer_report(dataset))


def _record(
    question_id: str,
    question: str,
    category: str,
    metric_eligible: bool,
    exclusion_reason: str | None,
    passages: list[SourcePassage],
    answer: GeneratedAnswer,
    evidence: EvidenceAssessment,
    corpus: ParentCorpus,
) -> AnswerEvaluationRecord:
    used_ids = set(answer.supporting_parent_chunk_ids)
    checks = automatic_checks(
        answer,
        passages,
        evidence,
        {passage.parent_chunk_id: corpus.text(passage.parent_chunk_id) for passage in passages},
    )
    return AnswerEvaluationRecord(
        question_id=question_id,
        question=question,
        category=_category(category),
        retrieval_metric_eligible=metric_eligible,
        retrieval_exclusion_reason=exclusion_reason,
        retrieved_parent_ranking=[
            RankedParent(
                rank=passage.rank,
                parent_chunk_id=passage.parent_chunk_id,
                document_id=passage.document_id,
                source_filename=passage.source_filename,
                page_start=passage.page_start,
                page_end=passage.page_end,
            )
            for passage in passages
        ],
        source_passages_retrieved=passages,
        source_passages_used=[
            passage for passage in passages if passage.parent_chunk_id in used_ids
        ],
        generated_answer=answer,
        evidence=evidence,
        automatic_checks=checks,
        human_review=HumanAnswerReview(),
    )


def _category(value: str) -> str:
    if value not in {"direct", "paraphrased", "conceptual"}:
        raise ValueError(f"unknown question category: {value}")
    return value


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _read_json(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _display_path(path: str) -> str:
    marker = "backend/"
    index = path.replace("\\", "/").rfind(marker)
    if index == -1:
        return path
    return path[index:]


def _count(records: list[AnswerEvaluationRecord], predicate) -> int:
    return sum(1 for record in records if predicate(record))


def _human(records: list[AnswerEvaluationRecord], field: str, expected: str) -> int:
    return sum(1 for record in records if getattr(record.human_review, field) == expected)


def _human_true(records: list[AnswerEvaluationRecord], field: str) -> int:
    return sum(1 for record in records if getattr(record.human_review, field) is True)


def _appropriate_abstentions(records: list[AnswerEvaluationRecord]) -> int:
    return sum(
        1
        for record in records
        if record.generated_answer.abstained
        and record.human_review.answerability in {"not_answerable", "contradictory"}
        and record.human_review.factual_support == "not_applicable"
    )
