"""Groq provider tests. These tests do not call the network or use a real key."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.answers.groq import (
    GroqAnswerError,
    GroqAnswerProvider,
    GroqConfigError,
    groq_provider_from_env,
    request_token_estimate,
    user_prompt,
)
from app.answers.groq_sample import (
    assert_sample_output,
    configuration_failure_sample,
    load_sample_questions,
    run_groq_sample,
    write_groq_sample,
)
from app.answers.schemas import AnswerGenerationRequest, SourcePassage

BACKEND_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = BACKEND_ROOT / "data" / "evaluation" / "amharic_retrieval_questions.json"
FAKE_KEY = "test-key-not-real"


class FakeCompletions:
    def __init__(self, owner: "FakeClient") -> None:
        self.owner = owner

    def create(self, **kwargs: object) -> "FakeCompletion":
        self.owner.calls.append(kwargs)
        if self.owner.script:
            item = self.owner.script.pop(0)
            if isinstance(item, BaseException):
                raise item
            return FakeCompletion(
                str(item),
                finish_reason=self.owner.finish_reason,
                reasoning=self.owner.reasoning,
            )
        if self.owner.error is not None:
            raise self.owner.error
        return FakeCompletion(
            self.owner.content,
            finish_reason=self.owner.finish_reason,
            reasoning=self.owner.reasoning,
        )


class FakeChat:
    def __init__(self, owner: "FakeClient") -> None:
        self.completions = FakeCompletions(owner)


class FakeClient:
    def __init__(
        self,
        content: str,
        error: BaseException | None = None,
        script: list[object] | None = None,
        finish_reason: str = "stop",
        reasoning: str | None = None,
    ) -> None:
        self.content = content
        self.error = error
        self.script = list(script or [])
        self.finish_reason = finish_reason
        self.reasoning = reasoning
        self.calls: list[dict[str, object]] = []
        self.chat = FakeChat(self)


class FakeCompletion:
    def __init__(
        self,
        content: object,
        finish_reason: str = "stop",
        reasoning: str | None = None,
    ) -> None:
        self.choices = [FakeChoice(content, finish_reason, reasoning)]


class FakeChoice:
    def __init__(
        self,
        content: object,
        finish_reason: str = "stop",
        reasoning: str | None = None,
    ) -> None:
        self.finish_reason = finish_reason
        self.message = FakeMessage(content, reasoning)


class FakeMessage:
    def __init__(self, content: object, reasoning: str | None = None) -> None:
        self.content = content
        self.reasoning = reasoning


class StatusError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


def _passage() -> SourcePassage:
    return SourcePassage(
        rank=1,
        document_id="10commandments",
        source_filename="10commandments.pdf",
        parent_chunk_id="10commandments:chunk-0032",
        page_start=11,
        page_end=11,
        extraction_method="ocr",
        source_quality_score=80,
        text="ሰንበትን የማክበር ትእዛዝ ከሕግ አስቀድሞ ተሰጠ",
        retrieved_units=[],
    )


def _request(passages: list[SourcePassage] | None = None, contradictory: bool = False) -> AnswerGenerationRequest:
    return AnswerGenerationRequest(
        question_id="direct-02",
        question="ሰንበትን የማክበር ትእዛዝ መቼ ተሰጠ?",
        language="am",
        passages=passages if passages is not None else [_passage()],
        contradictory=contradictory,
    )


def _model_json(**overrides: object) -> str:
    payload: dict[str, object] = {
        "answer_text": "ከተመለሰው ምንጭ የሰንበት ትእዛዝ ከሕግ አስቀድሞ ተሰጥቷል።",
        "abstained": False,
        "abstention_code": "none",
        "cited_parent_chunk_ids": ["10commandments:chunk-0032"],
    }
    payload.update(overrides)
    return json.dumps(payload, ensure_ascii=False)


def test_missing_api_key_and_model_fail_before_a_client_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.setattr("app.answers.env.backend_env_path", lambda: tmp_path / "missing.env")

    with pytest.raises(GroqConfigError) as missing_key:
        groq_provider_from_env()

    assert missing_key.value.code == "missing_api_key"
    assert FAKE_KEY not in str(missing_key.value)

    with pytest.raises(GroqConfigError) as missing_model:
        GroqAnswerProvider(api_key=FAKE_KEY, model_name="  ")

    assert missing_model.value.code == "missing_model"


def test_env_file_configures_the_model_without_overriding_the_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"GROQ_API_KEY={FAKE_KEY}\nGROQ_MODEL=file-model\nGROQ_TIMEOUT_SECONDS=15\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_MODEL", "process-model")
    monkeypatch.setattr("app.answers.env.backend_env_path", lambda: env_file)
    created: dict[str, object] = {}

    def factory(api_key: str, timeout: float) -> FakeClient:
        created["api_key"] = api_key
        created["timeout"] = timeout
        return FakeClient(_model_json())

    monkeypatch.setattr("app.answers.groq.build_groq_client", factory)

    provider = groq_provider_from_env()

    assert provider.model_name == "process-model"
    assert created["api_key"] == FAKE_KEY
    assert created["timeout"] == 15.0


def test_mocked_completion_copies_citation_metadata_and_hides_pages_from_the_prompt() -> None:
    client = FakeClient(_model_json())
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=client,
        timeout_seconds=15,
    )
    passage = _passage()

    answer = provider.generate(_request([passage]))

    assert client.calls[0]["model"] == "example-model"
    assert client.calls[0]["timeout"] == 15
    assert client.calls[0]["response_format"] == {"type": "json_object"}
    prompt = str(client.calls[0]["messages"])
    assert "page_start" not in prompt
    assert "10commandments.pdf" not in prompt
    assert passage.parent_chunk_id in prompt
    assert answer.provider_name == "groq"
    assert answer.model_name == "example-model"
    assert answer.abstained is False
    assert answer.answer_text != passage.text
    assert answer.citations[0].parent_chunk_id == passage.parent_chunk_id
    assert answer.citations[0].document_id == "10commandments"
    assert answer.citations[0].page_start == 11
    assert answer.citations[0].page_end == 11
    assert answer.citations[0].excerpt == passage.text
    assert client.calls[0]["max_completion_tokens"] == 512
    assert client.calls[0]["temperature"] == 0.5
    assert "reasoning_effort" not in client.calls[0]
    assert "ሰንበትን" in prompt
    assert any("\u1200" <= char <= "\u137f" for char in answer.answer_text)
    assert "answer_text must be nonempty" in prompt
    assert FAKE_KEY not in prompt
    assert FAKE_KEY not in answer.answer_text


def _ranked(rank: int, text: str) -> SourcePassage:
    return _passage().model_copy(
        update={
            "rank": rank,
            "parent_chunk_id": f"10commandments:chunk-{rank}",
            "text": text,
        }
    )


def test_prompt_uses_the_top_three_passages() -> None:
    passages = [_ranked(rank, f"ምንጭ {rank} ሰንበት ተሰጠ") for rank in range(1, 6)]
    client = FakeClient(
        _model_json(cited_parent_chunk_ids=["10commandments:chunk-1"])
    )
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="openai/gpt-oss-120b",
        client=client,
    )

    answer = provider.generate(_request(passages))
    prompt = str(client.calls[0]["messages"])

    assert provider.last_prompt_passage_ids == [
        "10commandments:chunk-1",
        "10commandments:chunk-2",
        "10commandments:chunk-3",
    ]
    assert "10commandments:chunk-4" not in prompt
    assert "10commandments:chunk-5" not in prompt
    assert passages[0].text in prompt
    assert answer.citations[0].parent_chunk_id == "10commandments:chunk-1"
    assert answer.citations[0].page_start == 11
    assert answer.citations[0].document_id == "10commandments"
    selected = passages[:3]
    assert provider.last_token_estimate == request_token_estimate(
        _request(passages),
        selected,
    )
    assert provider.last_token_estimate != sum(len(passage.text) for passage in selected)


def test_budget_drops_whole_passages_and_rejects_a_dropped_citation() -> None:
    passages = [_ranked(rank, f"አጭር ምንጭ {rank}") for rank in range(1, 4)]
    request = _request(passages)
    two_passage_cost = request_token_estimate(request, passages[:2])
    three_passage_cost = request_token_estimate(request, passages)
    client = FakeClient(
        _model_json(cited_parent_chunk_ids=["10commandments:chunk-3"])
    )
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=client,
        token_budget=two_passage_cost,
    )

    answer = provider.generate(request)
    prompt = str(client.calls[0]["messages"])

    assert three_passage_cost > two_passage_cost
    assert provider.last_prompt_passage_ids == [
        "10commandments:chunk-1",
        "10commandments:chunk-2",
    ]
    assert passages[0].text in prompt
    assert passages[1].text in prompt
    assert passages[2].text not in prompt
    assert answer.abstained is True
    assert answer.abstention_code == "rejected_citations"
    assert answer.citations == []
    assert "10commandments:chunk-3" in answer.rejected_citation_ids


def test_an_oversized_passage_is_not_truncated_or_sent() -> None:
    huge = _ranked(1, "ሀ" * 4000)
    request = _request([huge])
    client = FakeClient(_model_json())
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=client,
        token_budget=request_token_estimate(request, [huge]) - 1,
    )

    answer = provider.generate(request)

    assert client.calls == []
    assert answer.abstained is True
    assert answer.abstention_code == "missing_evidence"
    assert answer.citations == []
    assert "ሀሀ" not in answer.answer_text
    assert answer.abstention_reason == "No whole retrieved passage fits the token budget."


def test_gpt_oss_request_limits_reasoning_without_changing_the_model() -> None:
    client = FakeClient(_model_json())
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="openai/gpt-oss-120b",
        client=client,
    )

    provider.generate(_request())

    assert client.calls[0]["model"] == "openai/gpt-oss-120b"
    assert client.calls[0]["reasoning_effort"] == "low"
    assert client.calls[0]["include_reasoning"] is False
    assert client.calls[0]["max_completion_tokens"] == 512


def test_api_errors_do_not_expose_the_key_or_change_model() -> None:
    secret_message = f"bad key {FAKE_KEY}"
    cases = [
        (type("AuthenticationError", (Exception,), {})(secret_message), "authentication"),
        (type("RateLimitError", (Exception,), {})(secret_message), "rate_limit"),
        (type("APITimeoutError", (Exception,), {})(secret_message), "timeout"),
        (type("APIConnectionError", (Exception,), {})(secret_message), "network"),
        (type("NotFoundError", (Exception,), {})(secret_message), "model_unavailable"),
        (StatusError(400, secret_message), "model_unavailable"),
        (StatusError(401, secret_message), "authentication"),
        (StatusError(413, secret_message), "token_budget"),
        (StatusError(422, secret_message), "invalid_request"),
        (StatusError(500, secret_message), "server_error"),
        (type("InternalServerError", (Exception,), {"status_code": 503})(secret_message), "server_error"),
    ]
    for error, code in cases:
        provider = GroqAnswerProvider(
            api_key=FAKE_KEY,
            model_name="example-model",
            client=FakeClient("{}", error=error),
        )
        with pytest.raises(GroqAnswerError) as caught:
            provider.generate(_request())
        assert caught.value.code == code
        assert FAKE_KEY not in str(caught.value)
        assert "another-model" not in str(caught.value)


def test_empty_malformed_and_reasoning_responses_are_failures() -> None:
    empty = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=FakeClient(""),
    )
    missing = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=FakeClient("{}", script=[]),
    )
    missing._client.chat.completions.create = _raise_missing_choices  # type: ignore[method-assign]
    length = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=FakeClient("", finish_reason="length"),
    )
    reasoning = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=FakeClient(
            "",
            reasoning="ሰንበትን የማክበር ትእዛዝ ከሕግ አስቀድሞ ተሰጠ",
        ),
    )
    parts = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=FakeClient(_model_json()),
    )
    parts._client.content = [  # type: ignore[attr-defined]
        {"type": "reasoning", "text": "do not show"},
        {"type": "text", "text": _model_json()},
    ]

    with pytest.raises(GroqAnswerError) as empty_error:
        empty.generate(_request())
    with pytest.raises(GroqAnswerError) as missing_error:
        missing.generate(_request())
    with pytest.raises(GroqAnswerError) as length_error:
        length.generate(_request())
    with pytest.raises(GroqAnswerError) as reasoning_error:
        reasoning.generate(_request())
    answer = parts.generate(_request())

    assert empty_error.value.code == "invalid_response"
    assert "without answer text" in str(empty_error.value)
    assert missing_error.value.code == "invalid_response"
    assert "token limit" in str(length_error.value)
    assert reasoning_error.value.code == "invalid_response"
    assert "ሰንበት" not in str(reasoning_error.value)
    assert answer.abstained is False
    assert any("\u1200" <= char <= "\u137f" for char in answer.answer_text)


def _raise_missing_choices(**_kwargs: object) -> object:
    return type("NoChoices", (), {"choices": []})()


def test_retry_respects_retry_after_and_does_not_retry_authentication() -> None:
    waits: list[float] = []

    class Limited(Exception):
        def __init__(self) -> None:
            super().__init__(f"slow {FAKE_KEY}")
            self.status_code = 429
            self.response = type("Response", (), {"headers": {"retry-after": "1"}})()
            self.body = {"error": {"code": "rate_limit_exceeded", "message": FAKE_KEY}}

    limited = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="openai/gpt-oss-120b",
        client=FakeClient("", script=[Limited(), _model_json()]),
        sleeper=waits.append,
    )
    rejected = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="openai/gpt-oss-120b",
        client=FakeClient("", error=StatusError(401, FAKE_KEY)),
        sleeper=waits.append,
    )
    distant = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="openai/gpt-oss-120b",
        client=FakeClient(
            "",
            error=type(
                "RateLimitError",
                (Exception,),
                {
                    "status_code": 429,
                    "response": type("Response", (), {"headers": {"retry-after": "90"}})(),
                },
            )(),
        ),
        sleeper=waits.append,
    )

    answer = limited.generate(_request())
    with pytest.raises(GroqAnswerError) as auth_error:
        rejected.generate(_request())
    with pytest.raises(GroqAnswerError) as wait_error:
        distant.generate(_request())

    assert answer.model_name == "openai/gpt-oss-120b"
    assert waits == [1.0]
    assert len(limited._client.calls) == 2  # type: ignore[attr-defined]
    assert auth_error.value.code == "authentication"
    assert len(rejected._client.calls) == 1  # type: ignore[attr-defined]
    assert wait_error.value.code == "rate_limit"
    assert "90" in str(wait_error.value)
    assert FAKE_KEY not in str(wait_error.value)
    assert len(distant._client.calls) == 1  # type: ignore[attr-defined]


def test_unknown_chunk_id_abstains_without_keeping_the_invented_citation() -> None:
    client = FakeClient(
        _model_json(cited_parent_chunk_ids=["10commandments:chunk-9999"])
    )
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=client,
    )

    answer = provider.generate(_request())

    assert answer.abstained is True
    assert answer.abstention_code == "rejected_citations"
    assert answer.citations == []
    assert answer.rejected_citation_ids == ["10commandments:chunk-9999"]
    assert answer.supporting_parent_chunk_ids == []
    assert FAKE_KEY not in (answer.discarded_answer_text or "")


def test_missing_and_contradictory_evidence_abstain_without_calling_groq() -> None:
    client = FakeClient(_model_json())
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=client,
    )

    missing = provider.generate(_request([]))
    contradictory = provider.generate(_request(contradictory=True))

    assert client.calls == []
    assert missing.abstained is True
    assert missing.abstention_code == "missing_evidence"
    assert missing.citations == []
    assert contradictory.abstained is True
    assert contradictory.abstention_code == "contradictory_evidence"
    assert "አያስረግጡም" in contradictory.answer_text


def test_model_abstention_for_contradictory_passages_keeps_only_known_ids() -> None:
    second = _passage().model_copy(
        update={
            "rank": 2,
            "parent_chunk_id": "10commandments:chunk-0031",
            "text": "ሌላ የሰንበት አገላለጽ",
        }
    )
    client = FakeClient(
        _model_json(
            answer_text="ከተገኙ ምንጮች ይህን ጥያቄ ማረጋገጥ አልተቻለም።",
            abstained=True,
            abstention_code="contradictory_evidence",
            cited_parent_chunk_ids=[
                "10commandments:chunk-0032",
                "10commandments:chunk-0031",
            ],
        )
    )
    provider = GroqAnswerProvider(
        api_key=FAKE_KEY,
        model_name="example-model",
        client=client,
    )

    answer = provider.generate(_request([_passage(), second]))

    assert answer.abstained is True
    assert answer.abstention_code == "contradictory_evidence"
    assert answer.supporting_parent_chunk_ids == []
    assert {citation.role for citation in answer.citations} == {"unresolved_evidence"}
    assert [citation.page_start for citation in answer.citations] == [11, 11]


def test_sample_redacts_secrets_and_leaves_human_review_empty(tmp_path: Path) -> None:
    passage = _passage()
    questions = load_sample_questions(QUESTIONS_PATH)

    def retrieve(_question: str) -> list[SourcePassage]:
        return [passage]

    def generate(request: AnswerGenerationRequest):
        if request.question_id == "direct-01":
            raise GroqAnswerError("rate_limit", f"limited {FAKE_KEY}")
        return GroqAnswerProvider(
            api_key=FAKE_KEY,
            model_name="example-model",
            client=FakeClient(_model_json(answer_text=f"መልስ {FAKE_KEY}")),
        ).generate(request)

    payload = run_groq_sample(
        questions[:2],
        retrieve,
        generate,
        "example-model",
        secret=FAKE_KEY,
    )
    json_path = tmp_path / "groq-answer-sample.json"
    report_path = tmp_path / "groq-answer-sample-report.md"
    write_groq_sample(payload, json_path, report_path)
    written = json_path.read_text(encoding="utf-8")

    assert FAKE_KEY not in written
    assert "[redacted]" in written
    rows = {row["question_id"]: row for row in payload["records"]}
    assert rows["direct-01"]["generation_status"] == "api_error"
    assert rows["direct-01"]["error_code"] == "rate_limit"
    assert rows["direct-01"]["human_review"]["status"] == "pending"
    assert rows["direct-01"]["human_review"]["contains_unsupported_claims"] is None
    assert rows["direct-02"]["citations_match_retrieved_passages"] is True
    assert rows["direct-02"]["citations"][0]["page_start"] == 11
    assert rows["direct-02"]["human_review"]["factual_support"] is None
    with pytest.raises(ValueError, match="frozen"):
        assert_sample_output(BACKEND_ROOT / "data" / "evaluation" / "ground-truth-v3.json")
    failure = configuration_failure_sample(questions, "missing_api_key", "Set GROQ_API_KEY in backend/.env.")
    assert {row["generation_status"] for row in failure["records"]} == {"not_run"}
    assert "11" not in user_prompt(_request())
