"""Groq chat provider that can cite only retrieved parent passages."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from typing import Any, Literal

from app.answers.env import load_backend_env
from app.answers.providers import (
    ABSTAIN_CONTRADICTORY,
    ABSTAIN_MISSING,
    ConfiguredAnswerProvider,
)
from app.answers.schemas import (
    AnswerDraft,
    AnswerGenerationRequest,
    GeneratedAnswer,
    SourcePassage,
)

DEFAULT_TIMEOUT_SECONDS = 60.0
MAX_COMPLETION_TOKENS = 512
MAX_ATTEMPTS = 3
MAX_RETRY_WAIT_SECONDS = 15.0
MODEL_TOKEN_BUDGET = 8000
PROMPT_PASSAGE_LIMIT = 3
REQUEST_OVERHEAD_TOKENS = 256
_ABSTENTION_CODES = {"none", "missing_evidence", "contradictory_evidence"}
_RETRYABLE_CODES = {"timeout", "network", "rate_limit", "server_error", "conflict"}
_SAFE_BODY_CODES = {"rate_limit_exceeded"}


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
        sleeper: Callable[[float], None] | None = None,
        max_attempts: int = MAX_ATTEMPTS,
        token_budget: int = MODEL_TOKEN_BUDGET,
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
        if max_attempts < 1:
            raise GroqConfigError(
                "invalid_attempts",
                "Groq generation attempts must be at least one.",
            )
        if token_budget < MAX_COMPLETION_TOKENS + REQUEST_OVERHEAD_TOKENS:
            raise GroqConfigError(
                "invalid_token_budget",
                "The token budget must cover completion and request overhead.",
            )
        self.model_name = cleaned_model
        self._timeout_seconds = timeout_seconds
        self._sleeper = sleeper or time.sleep
        self._max_attempts = max_attempts
        self._token_budget = token_budget
        self.last_token_estimate: int | None = None
        self.last_prompt_passage_ids: list[str] = []
        self._client = client if client is not None else build_groq_client(
            cleaned_key,
            timeout_seconds,
        )

    def generate(self, request: AnswerGenerationRequest) -> GeneratedAnswer:
        self.last_token_estimate = None
        self.last_prompt_passage_ids = []
        if not request.passages:
            return _local_abstention(request, self.model_name, "missing_evidence")
        if request.contradictory:
            return _local_abstention(request, self.model_name, "contradictory_evidence")
        selected, estimate = select_prompt_passages(request, self._token_budget)
        self.last_token_estimate = estimate
        self.last_prompt_passage_ids = [passage.parent_chunk_id for passage in selected]
        if not selected:
            return _local_abstention(
                request,
                self.model_name,
                "missing_evidence",
                "No whole retrieved passage fits the token budget.",
            )
        limited = request.model_copy(update={"passages": selected})
        draft = self._draft_from_model(limited)
        answer = ConfiguredAnswerProvider(
            self.model_name,
            lambda _request: draft,
        ).generate(limited)
        return answer.model_copy(update={"provider_name": self.provider_name})

    def _draft_from_model(self, request: AnswerGenerationRequest) -> AnswerDraft:
        kwargs = _completion_kwargs(
            self.model_name,
            request,
            self._timeout_seconds,
        )
        for attempt in range(self._max_attempts):
            try:
                completion = self._client.chat.completions.create(**kwargs)
            except GroqAnswerError:
                raise
            except Exception as exc:
                mapped = map_groq_error(exc)
                delay = _retry_delay(exc, mapped.code, attempt)
                if attempt + 1 >= self._max_attempts or delay is None:
                    raise mapped from exc
                self._sleeper(delay)
                continue
            return parse_model_json(_completion_text(completion))
        raise GroqAnswerError("request_failed", "The Groq request failed.")


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

    status = _status_code(exc)
    name = type(exc).__name__
    body_code = _body_error_code(exc)
    if name == "APITimeoutError" or status == 408:
        return GroqAnswerError("timeout", "The Groq request timed out.")
    if name == "APIConnectionError":
        return GroqAnswerError("network", "The Groq service could not be reached.")
    if name in {"AuthenticationError", "PermissionDeniedError"} or status in {401, 403}:
        return GroqAnswerError("authentication", "Groq rejected the API key.")
    if name == "RateLimitError" or status == 429:
        return GroqAnswerError(
            "rate_limit",
            _rate_limit_message(_retry_after_seconds(exc)),
        )
    if status == 413 or body_code == "rate_limit_exceeded":
        return GroqAnswerError(
            "token_budget",
            "The request exceeds the configured model's token budget.",
        )
    if name in {"NotFoundError", "BadRequestError"} or status in {400, 404}:
        return GroqAnswerError(
            "model_unavailable",
            "The configured Groq model is unavailable. The request was not sent to another model.",
        )
    if name == "UnprocessableEntityError" or status == 422:
        return GroqAnswerError("invalid_request", "Groq rejected the answer request.")
    if name == "ConflictError" or status == 409:
        return GroqAnswerError(
            "conflict",
            "Groq could not complete the request because of a conflict.",
        )
    if name == "InternalServerError" or (status is not None and status >= 500):
        code = status if status is not None else 500
        return GroqAnswerError("server_error", f"Groq returned HTTP {code}.")
    return GroqAnswerError("request_failed", "The Groq request failed.")


def redact_secret(text: str, secret: str) -> str:
    if secret and secret in text:
        return text.replace(secret, "[redacted]")
    return text


SYSTEM_PROMPT = """Answer only from the supplied passages. Cite a parent_chunk_id only when that passage supports the answer, and never cite an id that was not supplied.
Answer in the requested language. For an Amharic question, answer_text must be nonempty Amharic.
Preserve qualifications and contradictions. Keep a statement the passage makes separate from a conclusion it does not establish.
If the passages are insufficient or contradict one another, abstain. Do not add teaching, quotations, document names, or page numbers.
Return JSON with keys answer_text, abstained, abstention_code, cited_parent_chunk_ids.
abstention_code is none, missing_evidence, or contradictory_evidence.
When abstained is false, abstention_code is none and the cited ids are only supporting passages.
When abstained is true, answer_text must be nonempty and the cited ids may name the insufficient or contradictory passages.
"""


def _completion_kwargs(
    model_name: str,
    request: AnswerGenerationRequest,
    timeout_seconds: float,
) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt(request)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.5,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "timeout": timeout_seconds,
    }
    if model_name.startswith("openai/gpt-oss"):
        kwargs["reasoning_effort"] = "low"
        kwargs["include_reasoning"] = False
    return kwargs


def _completion_text(completion: Any) -> str:
    try:
        choice = completion.choices[0]
        message = choice.message
    except (AttributeError, IndexError, TypeError) as exc:
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response without answer text.",
        ) from exc
    content = _visible_content(message)
    if not content.strip():
        if getattr(choice, "finish_reason", None) == "length":
            raise GroqAnswerError(
                "invalid_response",
                "Groq stopped at the token limit before it returned an answer.",
            )
        raise GroqAnswerError(
            "invalid_response",
            "Groq returned a response without answer text.",
        )
    return content


def _visible_content(message: Any) -> str:
    """Read the user-facing content. Reasoning text is never the answer."""

    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return ""


def _status_code(exc: BaseException) -> int | None:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status
    return None


def _body_error_code(exc: BaseException) -> str | None:
    body = getattr(exc, "body", None)
    if not isinstance(body, dict):
        return None
    error = body.get("error")
    if not isinstance(error, dict):
        return None
    code = error.get("code")
    if code in _SAFE_BODY_CODES:
        return str(code)
    return None


def _retry_after_seconds(exc: BaseException) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None or not hasattr(headers, "get"):
        return None
    raw = headers.get("retry-after")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value < 0:
        return None
    return value


def _rate_limit_message(retry_after: float | None) -> str:
    if retry_after is None:
        return "Groq rate limit was reached for the configured model."
    return (
        "Groq rate limit was reached for the configured model. "
        f"Retry after {retry_after:g} seconds."
    )


def _retry_delay(exc: BaseException, code: str, attempt: int) -> float | None:
    if code not in _RETRYABLE_CODES:
        return None
    retry_after = _retry_after_seconds(exc)
    if retry_after is not None:
        if retry_after > MAX_RETRY_WAIT_SECONDS:
            return None
        return retry_after
    return float(min(2**attempt, 4))


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


def estimate_text_tokens(text: str) -> int:
    """Return a conservative upper bound, not this model's tokenizer count.

    ASCII is charged at one token per two characters. Every other character,
    including Amharic, is charged at two tokens. The Groq tokenizer is not
    available locally, so this estimate is only used to avoid an oversized
    request.
    """

    ascii_chars = sum(1 for char in text if ord(char) < 128)
    other_chars = len(text) - ascii_chars
    return (ascii_chars + 1) // 2 + other_chars * 2


def request_token_estimate(
    request: AnswerGenerationRequest,
    passages: list[SourcePassage],
) -> int:
    """Estimate prompt, reserved completion, and chat overhead."""

    limited = request.model_copy(update={"passages": passages})
    prompt_tokens = estimate_text_tokens(SYSTEM_PROMPT) + estimate_text_tokens(
        user_prompt(limited)
    )
    return prompt_tokens + MAX_COMPLETION_TOKENS + REQUEST_OVERHEAD_TOKENS


def select_prompt_passages(
    request: AnswerGenerationRequest,
    token_budget: int = MODEL_TOKEN_BUDGET,
) -> tuple[list[SourcePassage], int]:
    """Keep the top three whole passages that fit the token budget.

    Lower-ranked passages are removed first. A passage is never cut in the
    middle, and a passage outside the top three is not substituted.
    """

    ordered = sorted(request.passages, key=lambda passage: passage.rank)
    selected = ordered[:PROMPT_PASSAGE_LIMIT]
    estimate = request_token_estimate(request, selected) if selected else 0
    while selected and estimate > token_budget:
        selected = selected[:-1]
        estimate = request_token_estimate(request, selected) if selected else 0
    return selected, estimate


def _local_abstention(
    request: AnswerGenerationRequest,
    model_name: str,
    code: Literal["missing_evidence", "contradictory_evidence"],
    reason: str | None = None,
) -> GeneratedAnswer:
    language = request.language
    if code == "contradictory_evidence":
        text = ABSTAIN_CONTRADICTORY[language]
        default_reason = "The request marked the retrieved passages as contradictory."
    else:
        text = ABSTAIN_MISSING[language]
        default_reason = "No retrieved source passage was supplied."
    reason = reason or default_reason
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
