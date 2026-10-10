# Source-grounded answer evaluation

Source-grounded answer evaluation for the frozen BAAI/bge-m3 dense retrieval run. Answers are produced by an extractive provider that quotes one retrieved parent passage or abstains. Human factual-support judgments are pending and are stored separately from automatic checks.

## Scope

- Retrieval model: `BAAI/bge-m3`
- Answer provider: `extractive-abstaining`
- Answer model: `none`
- Questions evaluated: 15
- Question file: `backend/data/evaluation/amharic_retrieval_questions.json`
- Retrieval results: `backend/data/evaluation/retrieval-evaluation-bge-m3.json`
- Parent corpus: `backend/data/processed/10commandments.chunks.json`

## Automatic checks

These checks confirm provenance. Teaching support is recorded only under human judgments.

| Check | Count |
| --- | ---: |
| Questions evaluated | 15 |
| Citation sets matching retrieved chunks | 15 |
| Excerpts that are exact substrings | 15 |
| Source passages identical to the stored corpus | 15 |
| Answer texts stored separately from source passages | 15 |
| Abstentions | 15 |
| Missing evidence | 0 |
| Contradictory or non-establishing evidence | 1 |
| Multiple passages left unresolved | 14 |
| Rejected citation selections | 0 |
| Single-passage quotations | 0 |
| Automatic provenance failures | 0 |

## Human judgments

A row counts in this section only when `human_review.status` is `reviewed`.

| Judgment | Count |
| --- | ---: |
| Reviewed records | 0 |
| Answers marked supported by sources | 0 |
| Answers marked partially supported | 0 |
| Answers marked unsupported | 0 |
| Important qualifications omitted | 0 |
| Unsupported claims present | 0 |
| Abstentions marked appropriate | 0 |
| Records awaiting human review | 15 |

## Questions

| Question | Evidence | Abstained | Citations match | Human review |
| --- | --- | --- | --- | --- |
| direct-01 | contradictory | contradictory_evidence | True | pending |
| direct-02 | multiple_passages | multiple_passages | True | pending |
| direct-03 | multiple_passages | multiple_passages | True | pending |
| direct-04 | multiple_passages | multiple_passages | True | pending |
| direct-05 | multiple_passages | multiple_passages | True | pending |
| paraphrased-01 | multiple_passages | multiple_passages | True | pending |
| paraphrased-02 | multiple_passages | multiple_passages | True | pending |
| paraphrased-03 | multiple_passages | multiple_passages | True | pending |
| paraphrased-04 | multiple_passages | multiple_passages | True | pending |
| paraphrased-05 | multiple_passages | multiple_passages | True | pending |
| conceptual-01 | multiple_passages | multiple_passages | True | pending |
| conceptual-02 | multiple_passages | multiple_passages | True | pending |
| conceptual-03 | multiple_passages | multiple_passages | True | pending |
| conceptual-04 | multiple_passages | multiple_passages | True | pending |
| conceptual-05 | multiple_passages | multiple_passages | True | pending |

## Failures awaiting human review

Every pending record still needs a person to judge answerability, factual support, omitted qualifications, and unsupported claims.

- `direct-01`: The evidence is marked as unable to establish one teaching from the available sources.
- `direct-02`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `direct-03`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `direct-04`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `direct-05`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `paraphrased-01`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `paraphrased-02`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `paraphrased-03`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `paraphrased-04`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `paraphrased-05`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `conceptual-01`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `conceptual-02`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `conceptual-03`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `conceptual-04`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.
- `conceptual-05`: More than one source passage is in scope. This provider does not choose among them or combine them into a new teaching.

## Limitations

- The extractive provider quotes a passage only when exactly one retrieved parent is in scope.
- The frozen top-five parent lists contain more than one passage, so those questions abstain.
- `direct-01` abstains because the frozen BGE-M3 result marks it metric-ineligible.
- Citation pages and document ids are copied from parent chunk records.
- No language-model provider or API key is configured for this run.
- Automatic checks do not accept a model's self-evaluation as factual support.
- OCR text, retrieval units, embeddings, ranking, and the retrieval benchmark files stay unchanged.

## Next step

A reviewer can mark each pending record, or name one supporting parent chunk for a later extractive quotation. A language model can be attached only through `ConfiguredAnswerProvider` with an explicit model name; its citations still have to match retrieved chunks before human review.
