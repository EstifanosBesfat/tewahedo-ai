# Ground-truth validation

The English concept checked here is the `review_focus` on each of the 15 evaluation questions. The Amharic passages are quoted from the prepared corpus of `10commandments.pdf`. OCR is left as extracted. Retrieval scores were not recalculated, and `retrieval-audit.json` was not changed.

| Question ID | Status | Source page(s) | Current ground truth correct? | Important context/issue |
|---|---|---|---|---|
| direct-01 | AMBIGUOUS | 4; 14; 2; 46–47 | No | "First commandment" is no other gods, honor of parents, and love of God. |
| direct-02 | PARTIALLY_SUPPORTED | 11 | Partly | The source dates the command to the end of creation, not only to "before the written Ten." |
| direct-03 | VERIFIED | 14 | Yes | Honor father and mother, with long life and well-being in the land God gives. |
| direct-04 | PARTIALLY_SUPPORTED | 15–16 | Partly | The teaching includes permitted killing under the old law and Christ's extension to anger. |
| direct-05 | VERIFIED | 34; 36 | Yes | False witness is called lying. The Exodus quotation line is OCR-corrupted. |
| paraphrased-01 | VERIFIED | 4 | Yes | Money is a rival idol. Ordinary use of money is explicitly not condemned. |
| paraphrased-02 | VERIFIED | 12 | Yes | The Sabbath is God's gift and a grace, not a burden imposed on people. |
| paraphrased-03 | PARTIALLY_SUPPORTED | 22–23 | Partly | Separation from God is killing the soul, and the text calls that worse than bodily killing. |
| paraphrased-04 | PARTIALLY_SUPPORTED | 24–25 | Partly | The duty is spiritual. Neglect and constant quarreling are called killing that life. |
| paraphrased-05 | PARTIALLY_SUPPORTED | 41 | Partly | Desire increases. Satisfaction is described as temporary, not as absent. |
| conceptual-01 | VERIFIED | 1 | Yes | The Ten Commandments are called covenants between God and human beings. |
| conceptual-02 | PARTIALLY_SUPPORTED | 2–3; 43 | Partly | The source says three commandments toward God and six toward people, then names the two loves. |
| conceptual-03 | VERIFIED | 12 | Yes | Bodily Sabbath rest signifies eternal spiritual rest. It is fulfilled as rest of the soul. |
| conceptual-04 | VERIFIED | 5 | Yes | Hiding or changing the truth to protect reputation is called worship of reputation. |
| conceptual-05 | VERIFIED | 7 | Yes | Self-worship is called greater and more dangerous than all other idols. |

## Summary

- VERIFIED: 8
- PARTIALLY_SUPPORTED: 6
- AMBIGUOUS: 1
- NOT_SUPPORTED: 0
- Questions requiring ground-truth revision: direct-01, direct-02, direct-04, paraphrased-03, paraphrased-04, paraphrased-05, conceptual-02
- Questions that should be excluded from retrieval metrics: direct-01
- Questions that are safe to use for retrieval evaluation: direct-03, direct-05, paraphrased-01, paraphrased-02, conceptual-01, conceptual-03, conceptual-04, conceptual-05

The existing Recall@1/3/5 figures of 5/14, 9/14, and 12/14 should be treated as provisional. They score the current labels, and six of the fourteen scored questions have English concepts that miss a qualification present in the Amharic.
