# Human review of source-grounded answers

Human review of the frozen BGE-M3 answer evaluation. A person records whether the retrieved passages establish an answer. Retrieval-metric eligibility stays on its own field, and no model approves the proposed answer.

- Source answer evaluation: `backend/data/evaluation/answer-evaluation-bge-m3.json`
- Source sha256: `f2ab1ad87fdac64bfdc7d05449699e2b4a36cf53d5fd60f3437d6da1df251784`
- Questions: 15
- Completed reviews: 0
- Pending cases: 15

## Answerability

These counts include completed reviews only.

| Answerable from available sources | Count |
| --- | ---: |
| yes | 0 |
| no | 0 |
| ambiguous | 0 |

## Selected evidence

| Evidence label | Count |
| --- | ---: |
| missing | 0 |
| contradictory | 0 |
| selected supporting passages | 0 |
| examined but not sufficient | 0 |
| proposed answers with an unsupported part | 0 |

## Retrieval eligibility

Retrieval-metric eligibility is copied from the frozen answer evaluation. It is not changed by a reviewer's answerability decision.

- Metric-eligible questions: 14
- Excluded from retrieval metrics: 1

## Completed reviews

No reviews are completed.

## Pending cases

- `direct-01`: retrieval metric eligible no; answerability pending
- `direct-02`: retrieval metric eligible yes; answerability pending
- `direct-03`: retrieval metric eligible yes; answerability pending
- `direct-04`: retrieval metric eligible yes; answerability pending
- `direct-05`: retrieval metric eligible yes; answerability pending
- `paraphrased-01`: retrieval metric eligible yes; answerability pending
- `paraphrased-02`: retrieval metric eligible yes; answerability pending
- `paraphrased-03`: retrieval metric eligible yes; answerability pending
- `paraphrased-04`: retrieval metric eligible yes; answerability pending
- `paraphrased-05`: retrieval metric eligible yes; answerability pending
- `conceptual-01`: retrieval metric eligible yes; answerability pending
- `conceptual-02`: retrieval metric eligible yes; answerability pending
- `conceptual-03`: retrieval metric eligible yes; answerability pending
- `conceptual-04`: retrieval metric eligible yes; answerability pending
- `conceptual-05`: retrieval metric eligible yes; answerability pending

## Scope

- Selected chunk IDs are accepted only when they appear in that question's retrieved parents.
- Document IDs and page ranges are copied from those parent records.
- Source text stays in the passage field, and the proposed answer stays in its own field.
- The starting answer-evaluation dataset is read and not replaced by this review file.
