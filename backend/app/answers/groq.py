"""Groq chat provider that can cite only retrieved parent passages."""

from __future__ import annotations

import json
import os
from typing import Any, Literal

from app.answers.env import load_backend_env
from app.answers.providers import (
    ABSTAIN_CONTRADICTORY,
    ABSTAIN_MISSING,
    ConfiguredAnswerProvider,
)
from app.answers.schemas import AnswerDraft, AnswerGenerationRequest, GeneratedAnswer

DEFAULT_TIMEOUT_SECONDS = 60.0
_ABSTENTION_CODES = {"none", "missing_evidence", "contradictory_evidence"}


class GroqConfigError(ValueError):
    """Local Groq settings are incomplete. The message never includes a key."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class GroqAnswerError(RuntimeError):
    """A Groq request failed. The message never includes a key or response body."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class GroqAnswerProvider:
    """Ask Groq for an answer, then attach citations from retrieved metadata.

    The configured model is used exactly as given. This provider does not
    substitute another model when Groq rejects the request.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model_name: str,
        client: Any | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        cleaned_key = api_key.strip()
        cleaned_model = model_name.strip()
        if not cleaned_key:
            raise GroqConfigError(
                "missing_api_key",
                "Set GROQ_API_KEY in backend/.env.",
            )
        if not cleaned_model:
            raise GroqConfigError(
                "missing_model",
                "Set GROQ_MODEL in backend/.env to a model id your Groq account can call.",
            )
        if timeout_seconds <= 0:
            raise GroqConfigError(
                "invalid_timeout",
                "GROQ_TIMEOUT_SECONDS must be greater than zero.",
            )
        self.model_name = cleaned_model
        self._timeout_seconds = timeout_seconds
        self._client = client if client is not None else build_groq_client(
            cleaned_key,
            timeout_seconds,
        )

    def generate(self, request: AnswerGenerationRequest) -> GeneratedAnswer:
        if not request.passages:
            return _local_abstention(request, self.model_name, "missing_evidence")
        if request.contradictory:
            return _local_abstention(request, self.model_name, "contradictory_evidence")
        draft = self._draft_from_model(request)
        answer = ConfiguredAnswerProvider(
            self.model_name,
            lambda _request: draft,
        ).generate(request)
        return answer.model_copy(update={"provider_name": self.provider_name})

    def _draft_from_model(self, request: AnswerGenerationRequest) -> AnswerDraft:
        try:
            completion = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt(request)},
                ],
                response_format={"type": "json_object"},
                timeout=self._timeout_seconds,
            )
        except GroqAnswerError:
            raise
        except Exception as exc:
            raise map_groq_error(exc) from exc
        content = _completion_text(completion)
        return parse_model_json(content)


def groq_provider_from_env() -> GroqAnswerProvider:
    """Build a provider from GROQ_API_KEY and GROQ_MODEL."""

    load_backend_env()
    timeout = _timeout_from_env(os.environ.get("GROQ_TIMEOUT_SECONDS"))
    return GroqAnswerProvider(
        api_key=os.environ.get("GROQ_API_KEY", ""),
        model_name=os.environ.get("GROQ_MODEL", ""),
        timeout_seconds=timeout,
    )


def build_groq_client(api_key: str, timeout_seconds: float) -> Any:
    from groq import Groq

    return Groq(
        api_key=api_key,
        timeout=timeout_seconds,
        max_retries=0,
    )


def user_prompt(request: AnswerGenerationRequest) -> str:
    """Show the question and passage text. Page numbers stay out of the prompt."""

    language = "Amharic" if request.language == "am" else "English"
    blocks = [
        f"parent_chunk_id: {passage.parent_chunk_id}\n{passage.text}"
        for passage in request.passages
    ]
    return (
        f"Answer language: {language}\n\n"
        f"Question:\n{request.question}\n\n"
        "Retrieved source passages:\n\n"
        + "\n\n".join(blocks)
    )


def parse_model_json(content: str) -> AnswerDraft:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response that was not JSON.",
        ) from exc
    if not isinstance(payload, dict):
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response that was not a JSON object.",
        )
    answer_text = payload.get("answer_text")
    abstained = payload.get("abstained")
    code = payload.get("abstention_code")
    cited = payload.get("cited_parent_chunk_ids")
    if (
        not isinstance(answer_text, str)
        or not isinstance(abstained, bool)
        or code not in _ABSTENTION_CODES
        or not isinstance(cited, list)
        or not all(isinstance(item, str) and item.strip() for item in cited)
    ):
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response that did not match the answer schema.",
        )
    if abstained and code == "none":
        raise GroqAnswerError(
            "invalid_response",
            "Groq marked the answer as an abstention without a reason code.",
        )
    if not abstained and code != "none":
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned an answer with an abstention reason.",
        )
    cleaned = answer_text.strip()
    if not cleaned:
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned an empty answer.",
        )
    role = "unresolved_evidence" if abstained else "supports_answer"
    return AnswerDraft(
        answer_text=cleaned,
        abstained=abstained,
        abstention_code=code,
        cited_parent_chunk_ids=[item.strip() for item in cited],
        citation_role=role,
    )


def map_groq_error(exc: BaseException) -> GroqAnswerError:
    """Translate a Groq exception into a fixed message with no response body."""

    status = getattr(exc, "status_code", None)
    name = type(exc).__name__
    if name == "APITimeoutError" or status == 408:
        return GroqAnswerError("timeout", "The Groq request timed out.")
    if name == "APIConnectionError":
        return GroqAnswerError("network", "The Groq service could not be reached.")
    if name in {"AuthenticationError", "PermissionDeniedError"} or status in {401, 403}:
        return GroqAnswerError("authentication", "Groq rejected the API key.")
    if name == "RateLimitError" or status == 429:
        return GroqAnswerError(
            "rate_limit",
            "Groq rate limit was reached for the configured model.",
        )
    if name in {"NotFoundError", "BadRequestError"} or status in {400, 404}:
        return GroqAnswerError(
            "model_unavailable",
            "The configured Groq model is unavailable. The request was not sent to another model.",
        )
    return GroqAnswerError("request_failed", "The Groq request failed.")


def redact_secret(text: str, secret: str) -> str:
    if secret and secret in text:
        return text.replace(secret, "[redacted]")
    return text


SYSTEM_PROMPT = """You answer from the retrieved Amharic source passages only.
The passages are candidates. Cite a parent_chunk_id only when that passage supports the answer.
Answer in the requested language.
Preserve qualifications and contradictions that are stated in the passages.
Keep an explicit source statement separate from a conclusion the passages do not establish.
When the passages are insufficient or contradict one another, abstain instead of choosing a teaching.
Do not add Orthodox teaching, biblical quotations, document names, or page numbers.
Do not cite a parent_chunk_id that was not supplied.
Return one JSON object with these keys:
answer_text, abstained, abstention_code, cited_parent_chunk_ids.
abstention_code must be none, missing_evidence, or contradictory_evidence.
When abstained is false, abstention_code is none and cited_parent_chunk_ids lists only supporting passages.
When abstained is true, cited_parent_chunk_ids may list the passages that were insufficient or contradictory.
"""


def _completion_text(completion: Any) -> str:
    try:
        content = completion.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response without answer text.",
        ) from exc
    if not isinstance(content, str) or not content.strip():
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response without answer text.",
        )
    return content


def _timeout_from_env(raw: str | None) -> float:
    if raw is None or not raw.strip():
        return DEFAULT_TIMEOUT_SECONDS
    try:
        return float(raw)
    except ValueError as exc:
        raise GroqConfigError(
            "invalid_timeout",
            "GROQ_TIMEOUT_SECONDS must be a number of seconds.",
        ) from exc


def _local_abstention(
    request: AnswerGenerationRequest,
    model_name: str,
    code: Literal["missing_evidence", "contradictory_evidence"],
) -> GeneratedAnswer:
    language = request.language
    if code == "contradictory_evidence":
        text = ABSTAIN_CONTRADICTORY[language]
        reason = "The request marked the retrieved passages as contradictory."
    else:
        text = ABSTAIN_MISSING[language]
        reason = "No retrieved source passage was supplied."
    return GeneratedAnswer(
        question_id=request.question_id,
        language=language,
        answer_text=text,
        abstained=True,
        abstention_code=code,
        abstention_reason=reason,
        citations=[],
        supporting_parent_chunk_ids=[],
        rejected_citation_ids=[],
        provider_name="groq",
        model_name=model_name,
    )
