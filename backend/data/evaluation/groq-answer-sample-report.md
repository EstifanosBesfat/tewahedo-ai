# Groq answer sample

Live BGE-M3 retrieval supplied the passages.

- Model: `openai/gpt-oss-120b`
- Questions: 4
- Generation succeeded: 0
- API or configuration errors: 4

Successful API calls are not theological judgments. Human review fields stay empty.

| Question | Status | Abstained | Citations match | Amharic answer | Latency seconds | Human review |
| --- | --- | --- | --- | --- | ---: | --- |
| direct-01 | api_error | None | None | False | 20.486 | pending |
| direct-02 | api_error | None | None | False | 16.081 | pending |
| direct-05 | api_error | None | None | False | 0.878 | pending |
| paraphrased-01 | api_error | None | None | False | 0.872 | pending |

## Notes

- `direct-01`: invalid_response. Groq returned an empty answer.
- `direct-02`: request_failed. The Groq request failed.
- `direct-05`: request_failed. The Groq request failed.
- `paraphrased-01`: rate_limit. Groq rate limit was reached for the configured model.
