"""Run a small live Groq sample without replacing frozen evaluations."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from app.answers.citations import automatic_checks
from app.answers.dataset import assert_writable_output
from app.answers.groq import GroqAnswerError, redact_secret
from app.answers.providers import assess_evidence
from app.answers.review import PROTECTED_REVIEW_SOURCES
from app.answers.schemas import (
    AnswerGenerationRequest,
    GeneratedAnswer,
    HumanAnswerReview,
    SourcePassage,
)

SAMPLE_QUESTION_IDS = (
    "direct-01",
    "direct-02",
    "direct-05",
    "paraphrased-01",
)
SAMPLE_OUTPUT_NAME = "groq-answer-sample.json"
SAMPLE_REPORT_NAME = "groq-answer-sample-report.md"
PROTECTED_SAMPLE_OUTPUTS = PROTECTED_REVIEW_SOURCES | {
    "groq-answer-sample.json",
}


def assert_sample_output(path: Path) -> None:
    assert_writable_output(path)
    if path.name in PROTECTED_SAMPLE_OUTPUTS and path.name != SAMPLE_OUTPUT_NAME:
        raise ValueError(f"{path.name} is a frozen evaluation artifact")
    if path.name == SAMPLE_REPORT_NAME:
        return
    if path.name != SAMPLE_OUTPUT_NAME:
        raise ValueError(f"{path.name} is not the Groq sample output")


def load_sample_questions(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    by_id = {
        str(item["question_id"]): item
        for item in payload["questions"]
    }
    return [
        {
            "question_id": question_id,
            "question": str(by_id[question_id]["question"]),
            "category": str(by_id[question_id]["category"]),
        }
        for question_id in SAMPLE_QUESTION_IDS
    ]


def configuration_failure_sample(
    questions: Sequence[Mapping[str, str]],
    error_code: str,
    error_message: str,
    secret: str = "",
) -> dict[str, object]:
    message = redact_secret(error_message, secret)
    records = [
        _empty_record(question, "not_run", message, error_code)
        for question in questions
    ]
    payload = _payload(None, records, "Groq was not called.")
    payload["retrieval"] = "not run"
    return payload


def run_groq_sample(
    questions: Sequence[Mapping[str, str]],
    retrieve: Callable[[str], list[SourcePassage]],
    generate: Callable[[AnswerGenerationRequest], GeneratedAnswer],
    model_name: str,
    secret: str = "",
) -> dict[str, object]:
    """Retrieve live passages and generate one answer per sample question."""

    records: list[dict[str, object]] = []
    for question in questions:
        started = time.perf_counter()
        try:
            passages = retrieve(str(question["question"]))
            request = AnswerGenerationRequest(
                question_id=str(question["question_id"]),
                question=str(question["question"]),
                language="am",
                passages=passages,
            )
            answer = generate(request)
        except GroqAnswerError as exc:
            elapsed = round(time.perf_counter() - started, 3)
            records.append(
                _empty_record(
                    question,
                    "api_error",
                    redact_secret(str(exc), secret),
                    exc.code,
                    elapsed,
                )
            )
            continue
        elapsed = round(time.perf_counter() - started, 3)
        records.append(_success_record(question, answer, passages, elapsed, secret))
    return _payload(model_name, records, "Live BGE-M3 retrieval supplied the passages.")


def render_groq_sample_report(payload: Mapping[str, object]) -> str:
    records = payload["records"]
    if not isinstance(records, list):
        raise ValueError("sample payload is missing records")
    succeeded = [row for row in records if row["generation_status"] == "succeeded"]
    errors = [row for row in records if row["generation_status"] != "succeeded"]
    lines = [
        "# Groq answer sample",
        "",
        str(payload["description"]),
        "",
        f"- Model: `{payload['model_name'] or 'none'}`",
        f"- Questions: {len(records)}",
        f"- Generation succeeded: {len(succeeded)}",
        f"- API or configuration errors: {len(errors)}",
        "",
        "Successful API calls are not theological judgments. Human review fields stay empty.",
        "",
        "| Question | Status | Abstained | Citations match | Amharic answer | Latency seconds | Human review |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in records:
        if not isinstance(row, dict):
            continue
        lines.append(
            "| {question_id} | {status} | {abstained} | {citations} | {amharic} | {latency} | {review} |".format(
                question_id=row["question_id"],
                status=row["generation_status"],
                abstained=row["abstained"],
                citations=row["citations_match_retrieved_passages"],
                amharic=row["answer_contains_amharic"],
                latency=row["latency_seconds"],
                review=row["human_review"]["status"],
            )
        )
    lines.extend(["", "## Notes", ""])
    for row in records:
        if not isinstance(row, dict):
            continue
        if row["error_code"]:
            lines.append(
                f"- `{row['question_id']}`: {row['error_code']}. {row['error_message']}"
            )
        else:
            lines.append(
                f"- `{row['question_id']}` awaits human review for unsupported claims and missing qualifications."
            )
    lines.append("")
    return "\n".join(lines)


def write_groq_sample(payload: Mapping[str, object], json_path: Path, report_path: Path) -> None:
    assert_sample_output(json_path)
    if report_path.name != SAMPLE_REPORT_NAME:
        raise ValueError(f"{report_path.name} is not the Groq sample report")
    assert_writable_output(report_path)
    _write_text(
        json_path,
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )
    _write_text(report_path, render_groq_sample_report(payload))


def _payload(
    model_name: str | None,
    records: list[dict[str, object]],
    description: str,
) -> dict[str, object]:
    return {
        "schema_version": "1",
        "description": description,
        "provider": "groq",
        "model_name": model_name,
        "retrieval": "live BGE-M3 parent passages",
        "question_count": len(records),
        "records": records,
    }


def _empty_record(
    question: Mapping[str, str],
    status: str,
    message: str,
    error_code: str,
    latency: float | None = None,
) -> dict[str, object]:
    return {
        "question_id": question["question_id"],
        "question": question["question"],
        "category": question["category"],
        "generation_status": status,
        "error_code": error_code,
        "error_message": message,
        "latency_seconds": latency,
        "language": "am",
        "abstained": None,
        "answer_text": "",
        "answer_contains_amharic": False,
        "citations": [],
        "citations_match_retrieved_passages": None,
        "source_passages": [],
        "human_review": HumanAnswerReview().model_dump(mode="json"),
    }


def _success_record(
    question: Mapping[str, str],
    answer: GeneratedAnswer,
    passages: Sequence[SourcePassage],
    latency: float,
    secret: str,
) -> dict[str, object]:
    evidence = assess_evidence(passages)
    checks = automatic_checks(answer, passages, evidence)
    answer_text = redact_secret(answer.answer_text, secret)
    return {
        "question_id": question["question_id"],
        "question": question["question"],
        "category": question["category"],
        "generation_status": "succeeded",
        "error_code": None,
        "error_message": None,
        "latency_seconds": latency,
        "language": answer.language,
        "abstained": answer.abstained,
        "abstention_code": answer.abstention_code,
        "answer_text": answer_text,
        "answer_contains_amharic": _contains_amharic(answer_text),
        "answer_text_differs_from_source": checks.answer_text_differs_from_each_source_passage,
        "citations_match_retrieved_passages": checks.citations_match_retrieved_passages,
        "citations": [
            citation.model_dump(mode="json") for citation in answer.citations
        ],
        "source_passages": [
            {
                "rank": passage.rank,
                "parent_chunk_id": passage.parent_chunk_id,
                "document_id": passage.document_id,
                "source_filename": passage.source_filename,
                "page_start": passage.page_start,
                "page_end": passage.page_end,
                "text": passage.text,
            }
            for passage in passages
        ],
        "human_review": HumanAnswerReview().model_dump(mode="json"),
    }


def _contains_amharic(text: str) -> bool:
    return any("\u1200" <= character <= "\u137F" for character in text)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)
