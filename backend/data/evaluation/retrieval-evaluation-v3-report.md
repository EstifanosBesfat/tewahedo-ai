# E5 baseline on ground-truth-v3

This run uses the same 182 retrieval units, `intfloat/multilingual-e5-small`, the same query processing, the same top-20 unit search, and the same collapse to five parent chunks. The only scoring change is `paraphrased-05`: `chunk-0101` and `chunk-0102` are both relevant, and either parent inside the top k counts as a hit.

`direct-01` stays excluded. The denominator is 14.

## Final recall

| Metric | Result |
| --- | --- |
| Recall@1 | **9/14** |
| Recall@3 | **12/14** |
| Recall@5 | **13/14** |

Previous official ground-truth-v2:

R@1 = 8/14

R@3 = 11/14

R@5 = 12/14

Final ground-truth-v3:

R@1 = 9/14

R@3 = 12/14

R@5 = 13/14

Every parent ranking is identical to the official v2 run. Retrieval did not change. The score rises by one at each cutoff because `paraphrased-05` is now a hit.

## Remaining misses at Recall@5

`direct-05` is the only metric-eligible miss. Its relevant parents, `chunk-0085` and `chunk-0089`, are still outside the top five parents.

## Questions that became worse

None. The other 13 metric-eligible questions keep the same hit pattern at k=1, k=3, and k=5.

## paraphrased-05

The question text is unchanged.

Relevant parents are now `10commandments:chunk-0101` and `10commandments:chunk-0102`, both on page 41 of `10commandments.pdf`. `chunk-0102` remains relevant. `chunk-0101` was added because human review of its own Amharic confirmed that it independently supports the expected concept.

Official v2, when only `chunk-0102` was relevant: miss / miss / miss.

Ground-truth-v3, when either parent counts: hit / hit / hit.

The collapsed parents are:

| Parent rank | Parent chunk | Relevant |
| --- | --- | --- |
| 1 | `10commandments:chunk-0101` | yes |
| 2 | `10commandments:chunk-0099` | no |
| 3 | `10commandments:chunk-0098` | no |
| 4 | `10commandments:chunk-0094` | no |
| 5 | `10commandments:chunk-0096` | no |

`chunk-0101` is parent rank 1, so the question hits at k=1, k=3, and k=5. `chunk-0102` is still retrieved, at unit rank 10, which is outside the five parents used for recall. The hit rule counts the question when either relevant parent is inside the cutoff. Here the counted parent is `chunk-0101`.

## Result for each metric-eligible question

| Question | Recall@1 | Recall@3 | Recall@5 | Compared with official v2 |
| --- | --- | --- | --- | --- |
| direct-02 | hit | hit | hit | unchanged |
| direct-03 | miss | hit | hit | unchanged |
| direct-04 | hit | hit | hit | unchanged |
| direct-05 | miss | miss | miss | unchanged |
| paraphrased-01 | hit | hit | hit | unchanged |
| paraphrased-02 | hit | hit | hit | unchanged |
| paraphrased-03 | miss | hit | hit | unchanged |
| paraphrased-04 | miss | hit | hit | unchanged |
| paraphrased-05 | hit | hit | hit | improved |
| conceptual-01 | miss | miss | hit | unchanged |
| conceptual-02 | hit | hit | hit | unchanged |
| conceptual-03 | hit | hit | hit | unchanged |
| conceptual-04 | hit | hit | hit | unchanged |
| conceptual-05 | hit | hit | hit | unchanged |

## Denominator

The benchmark still has 15 questions. `direct-01` is ambiguous and `metric_eligible` is false. Recall uses the other 14 questions.
