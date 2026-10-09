# Official multilingual-e5-small retrieval baseline

This run scores the existing 182 retrieval units with intfloat/multilingual-e5-small against the approved ground-truth-v2 benchmark. direct-01 stays ambiguous and is excluded from the denominator.

## Final recall

| Metric | Result |
| --- | --- |
| Recall@1 | **8/14** |
| Recall@3 | **11/14** |
| Recall@5 | **12/14** |

Settings: collection tewahedo_multilingual_e5_small_v1, store backend/data/vectorstore/multilingual-e5-small-units, 182 units, query text stripped and then given the existing E5 query prefix, top 20 units collapsed to 5 unique parent chunks. A hit is a relevant parent chunk inside that cutoff. No retrieval result was edited.

## Comparison

Previous provisional:

R@1 = 7/14

R@3 = 10/14

R@5 = 12/14

Final ground-truth-v2:

R@1 = 8/14

R@3 = 11/14

R@5 = 12/14

Every parent ranking is identical to the provisional unit comparison. The retrieval order did not change. Recall@1 and Recall@3 each rise by one because paraphrased-02 now counts 10commandments:chunk-0033, which the approved ground truth cites and which was already parent rank 1. The provisional audit had treated only 10commandments:chunk-0034 as verified, so that question was a hit at 5 and a miss at 1 and 3. Recall@5 is unchanged.

## Result for each metric-eligible question

| Question | Recall@1 | Recall@3 | Recall@5 | Compared with provisional |
| --- | --- | --- | --- | --- |
| direct-02 | hit | hit | hit | unchanged |
| direct-03 | miss | hit | hit | unchanged |
| direct-04 | hit | hit | hit | unchanged |
| direct-05 | miss | miss | miss | unchanged |
| paraphrased-01 | hit | hit | hit | unchanged |
| paraphrased-02 | hit | hit | hit | improved |
| paraphrased-03 | miss | hit | hit | unchanged |
| paraphrased-04 | miss | hit | hit | unchanged |
| paraphrased-05 | miss | miss | miss | unchanged |
| conceptual-01 | miss | miss | hit | unchanged |
| conceptual-02 | hit | hit | hit | unchanged |
| conceptual-03 | hit | hit | hit | unchanged |
| conceptual-04 | hit | hit | hit | unchanged |
| conceptual-05 | hit | hit | hit | unchanged |

## Questions still missed at Recall@5

- direct-05. Relevant parents are 10commandments:chunk-0085 and 10commandments:chunk-0089. The top five parents are chunk-0013, chunk-0007, chunk-0086, chunk-0012, and chunk-0087. chunk-0089 first appears at unit rank 8, and chunk-0085 at unit rank 13.
- paraphrased-05. The approved relevant parent is 10commandments:chunk-0102 only. It first appears at unit rank 10. The top parent is 10commandments:chunk-0101, which is not in the approved relevant set.

## Improved or worsened

Improved: paraphrased-02 only. It changes from miss/miss/hit to hit/hit/hit. Parent rank 1 is 10commandments:chunk-0033, and parent rank 4 is 10commandments:chunk-0034. Both are relevant in the approved ground truth.

Worsened: none.

The other 13 metric-eligible questions keep the same hit pattern at k=1, k=3, and k=5.

## Retrieved parents and units

Parent rank is the order after collapsing duplicate units of the same parent. Unit rank is the raw search order before that collapse. Only the first five unique parents are used for recall.

### direct-02

Matched relevant parents: 10commandments:chunk-0032, 10commandments:chunk-0031.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0032 |
| 2 | 10commandments:chunk-0039 |
| 3 | 10commandments:chunk-0031 |
| 4 | 10commandments:chunk-0035 |
| 5 | 10commandments:chunk-0037 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0032:unit-01 | 10commandments:chunk-0032 |
| 2 | 10commandments:chunk-0039:unit-02 | 10commandments:chunk-0039 |
| 3 | 10commandments:chunk-0031:unit-02 | 10commandments:chunk-0031 |
| 4 | 10commandments:chunk-0035:unit-01 | 10commandments:chunk-0035 |
| 5 | 10commandments:chunk-0037:unit-01 | 10commandments:chunk-0037 |
| 6 | 10commandments:chunk-0034:unit-02 | 10commandments:chunk-0034 |
| 7 | 10commandments:chunk-0006:unit-03 | 10commandments:chunk-0006 |
| 8 | 10commandments:chunk-0032:unit-02 | 10commandments:chunk-0032 |
| 9 | 10commandments:chunk-0033:unit-01 | 10commandments:chunk-0033 |
| 10 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 11 | 10commandments:chunk-0038:unit-01 | 10commandments:chunk-0038 |
| 12 | 10commandments:chunk-0034:unit-01 | 10commandments:chunk-0034 |
| 13 | 10commandments:chunk-0045:unit-02 | 10commandments:chunk-0045 |
| 14 | 10commandments:chunk-0044:unit-01 | 10commandments:chunk-0044 |
| 15 | 10commandments:chunk-0007:unit-01 | 10commandments:chunk-0007 |
| 16 | 10commandments:chunk-0002:unit-02 | 10commandments:chunk-0002 |
| 17 | 10commandments:chunk-0039:unit-01 | 10commandments:chunk-0039 |
| 18 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 19 | 10commandments:chunk-0040:unit-01 | 10commandments:chunk-0040 |
| 20 | 10commandments:chunk-0113:unit-01 | 10commandments:chunk-0113 |

### direct-03

Matched relevant parents: 10commandments:chunk-0040.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0044 |
| 2 | 10commandments:chunk-0040 |
| 3 | 10commandments:chunk-0041 |
| 4 | 10commandments:chunk-0007 |
| 5 | 10commandments:chunk-0032 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0044:unit-01 | 10commandments:chunk-0044 |
| 2 | 10commandments:chunk-0040:unit-01 | 10commandments:chunk-0040 |
| 3 | 10commandments:chunk-0041:unit-01 | 10commandments:chunk-0041 |
| 4 | 10commandments:chunk-0007:unit-01 | 10commandments:chunk-0007 |
| 5 | 10commandments:chunk-0032:unit-01 | 10commandments:chunk-0032 |
| 6 | 10commandments:chunk-0005:unit-01 | 10commandments:chunk-0005 |
| 7 | 10commandments:chunk-0063:unit-01 | 10commandments:chunk-0063 |
| 8 | 10commandments:chunk-0111:unit-01 | 10commandments:chunk-0111 |
| 9 | 10commandments:chunk-0106:unit-01 | 10commandments:chunk-0106 |
| 10 | 10commandments:chunk-0006:unit-03 | 10commandments:chunk-0006 |
| 11 | 10commandments:chunk-0043:unit-02 | 10commandments:chunk-0043 |
| 12 | 10commandments:chunk-0047:unit-01 | 10commandments:chunk-0047 |
| 13 | 10commandments:chunk-0113:unit-01 | 10commandments:chunk-0113 |
| 14 | 10commandments:chunk-0002:unit-01 | 10commandments:chunk-0002 |
| 15 | 10commandments:chunk-0005:unit-02 | 10commandments:chunk-0005 |
| 16 | 10commandments:chunk-0045:unit-02 | 10commandments:chunk-0045 |
| 17 | 10commandments:chunk-0031:unit-02 | 10commandments:chunk-0031 |
| 18 | 10commandments:chunk-0082:unit-02 | 10commandments:chunk-0082 |
| 19 | 10commandments:chunk-0051:unit-01 | 10commandments:chunk-0051 |
| 20 | 10commandments:chunk-0042:unit-01 | 10commandments:chunk-0042 |

### direct-04

Matched relevant parents: 10commandments:chunk-0045, 10commandments:chunk-0047.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0045 |
| 2 | 10commandments:chunk-0051 |
| 3 | 10commandments:chunk-0047 |
| 4 | 10commandments:chunk-0054 |
| 5 | 10commandments:chunk-0022 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0045:unit-01 | 10commandments:chunk-0045 |
| 2 | 10commandments:chunk-0051:unit-01 | 10commandments:chunk-0051 |
| 3 | 10commandments:chunk-0047:unit-01 | 10commandments:chunk-0047 |
| 4 | 10commandments:chunk-0047:unit-02 | 10commandments:chunk-0047 |
| 5 | 10commandments:chunk-0054:unit-01 | 10commandments:chunk-0054 |
| 6 | 10commandments:chunk-0022:unit-01 | 10commandments:chunk-0022 |
| 7 | 10commandments:chunk-0111:unit-01 | 10commandments:chunk-0111 |
| 8 | 10commandments:chunk-0076:unit-01 | 10commandments:chunk-0076 |
| 9 | 10commandments:chunk-0055:unit-01 | 10commandments:chunk-0055 |
| 10 | 10commandments:chunk-0054:unit-02 | 10commandments:chunk-0054 |
| 11 | 10commandments:chunk-0106:unit-01 | 10commandments:chunk-0106 |
| 12 | 10commandments:chunk-0098:unit-01 | 10commandments:chunk-0098 |
| 13 | 10commandments:chunk-0045:unit-02 | 10commandments:chunk-0045 |
| 14 | 10commandments:chunk-0069:unit-01 | 10commandments:chunk-0069 |
| 15 | 10commandments:chunk-0007:unit-01 | 10commandments:chunk-0007 |
| 16 | 10commandments:chunk-0005:unit-01 | 10commandments:chunk-0005 |
| 17 | 10commandments:chunk-0040:unit-01 | 10commandments:chunk-0040 |
| 18 | 10commandments:chunk-0057:unit-01 | 10commandments:chunk-0057 |
| 19 | 10commandments:chunk-0058:unit-01 | 10commandments:chunk-0058 |
| 20 | 10commandments:chunk-0058:unit-02 | 10commandments:chunk-0058 |

### direct-05

Matched relevant parents: none.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0013 |
| 2 | 10commandments:chunk-0007 |
| 3 | 10commandments:chunk-0086 |
| 4 | 10commandments:chunk-0012 |
| 5 | 10commandments:chunk-0087 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0013:unit-01 | 10commandments:chunk-0013 |
| 2 | 10commandments:chunk-0007:unit-01 | 10commandments:chunk-0007 |
| 3 | 10commandments:chunk-0086:unit-02 | 10commandments:chunk-0086 |
| 4 | 10commandments:chunk-0012:unit-01 | 10commandments:chunk-0012 |
| 5 | 10commandments:chunk-0087:unit-01 | 10commandments:chunk-0087 |
| 6 | 10commandments:chunk-0093:unit-01 | 10commandments:chunk-0093 |
| 7 | 10commandments:chunk-0088:unit-01 | 10commandments:chunk-0088 |
| 8 | 10commandments:chunk-0089:unit-02 | 10commandments:chunk-0089 |
| 9 | 10commandments:chunk-0054:unit-01 | 10commandments:chunk-0054 |
| 10 | 10commandments:chunk-0111:unit-01 | 10commandments:chunk-0111 |
| 11 | 10commandments:chunk-0081:unit-01 | 10commandments:chunk-0081 |
| 12 | 10commandments:chunk-0076:unit-01 | 10commandments:chunk-0076 |
| 13 | 10commandments:chunk-0085:unit-01 | 10commandments:chunk-0085 |
| 14 | 10commandments:chunk-0089:unit-01 | 10commandments:chunk-0089 |
| 15 | 10commandments:chunk-0107:unit-01 | 10commandments:chunk-0107 |
| 16 | 10commandments:chunk-0108:unit-01 | 10commandments:chunk-0108 |
| 17 | 10commandments:chunk-0047:unit-01 | 10commandments:chunk-0047 |
| 18 | 10commandments:chunk-0045:unit-02 | 10commandments:chunk-0045 |
| 19 | 10commandments:chunk-0110:unit-01 | 10commandments:chunk-0110 |
| 20 | 10commandments:chunk-0109:unit-01 | 10commandments:chunk-0109 |

### paraphrased-01

Matched relevant parents: 10commandments:chunk-0009, 10commandments:chunk-0010.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0009 |
| 2 | 10commandments:chunk-0010 |
| 3 | 10commandments:chunk-0016 |
| 4 | 10commandments:chunk-0084 |
| 5 | 10commandments:chunk-0021 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0009:unit-01 | 10commandments:chunk-0009 |
| 2 | 10commandments:chunk-0010:unit-01 | 10commandments:chunk-0010 |
| 3 | 10commandments:chunk-0016:unit-02 | 10commandments:chunk-0016 |
| 4 | 10commandments:chunk-0084:unit-01 | 10commandments:chunk-0084 |
| 5 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 6 | 10commandments:chunk-0047:unit-02 | 10commandments:chunk-0047 |
| 7 | 10commandments:chunk-0068:unit-01 | 10commandments:chunk-0068 |
| 8 | 10commandments:chunk-0053:unit-01 | 10commandments:chunk-0053 |
| 9 | 10commandments:chunk-0013:unit-02 | 10commandments:chunk-0013 |
| 10 | 10commandments:chunk-0077:unit-01 | 10commandments:chunk-0077 |
| 11 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 12 | 10commandments:chunk-0061:unit-01 | 10commandments:chunk-0061 |
| 13 | 10commandments:chunk-0067:unit-01 | 10commandments:chunk-0067 |
| 14 | 10commandments:chunk-0101:unit-01 | 10commandments:chunk-0101 |
| 15 | 10commandments:chunk-0033:unit-01 | 10commandments:chunk-0033 |
| 16 | 10commandments:chunk-0082:unit-02 | 10commandments:chunk-0082 |
| 17 | 10commandments:chunk-0066:unit-01 | 10commandments:chunk-0066 |
| 18 | 10commandments:chunk-0080:unit-02 | 10commandments:chunk-0080 |
| 19 | 10commandments:chunk-0020:unit-01 | 10commandments:chunk-0020 |
| 20 | 10commandments:chunk-0100:unit-02 | 10commandments:chunk-0100 |

### paraphrased-02

Matched relevant parents: 10commandments:chunk-0033, 10commandments:chunk-0034.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0033 |
| 2 | 10commandments:chunk-0036 |
| 3 | 10commandments:chunk-0039 |
| 4 | 10commandments:chunk-0034 |
| 5 | 10commandments:chunk-0035 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0033:unit-01 | 10commandments:chunk-0033 |
| 2 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 3 | 10commandments:chunk-0039:unit-01 | 10commandments:chunk-0039 |
| 4 | 10commandments:chunk-0034:unit-01 | 10commandments:chunk-0034 |
| 5 | 10commandments:chunk-0035:unit-01 | 10commandments:chunk-0035 |
| 6 | 10commandments:chunk-0038:unit-01 | 10commandments:chunk-0038 |
| 7 | 10commandments:chunk-0032:unit-01 | 10commandments:chunk-0032 |
| 8 | 10commandments:chunk-0080:unit-02 | 10commandments:chunk-0080 |
| 9 | 10commandments:chunk-0084:unit-01 | 10commandments:chunk-0084 |
| 10 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 11 | 10commandments:chunk-0100:unit-02 | 10commandments:chunk-0100 |
| 12 | 10commandments:chunk-0077:unit-01 | 10commandments:chunk-0077 |
| 13 | 10commandments:chunk-0107:unit-02 | 10commandments:chunk-0107 |
| 14 | 10commandments:chunk-0037:unit-01 | 10commandments:chunk-0037 |
| 15 | 10commandments:chunk-0065:unit-02 | 10commandments:chunk-0065 |
| 16 | 10commandments:chunk-0057:unit-01 | 10commandments:chunk-0057 |
| 17 | 10commandments:chunk-0048:unit-01 | 10commandments:chunk-0048 |
| 18 | 10commandments:chunk-0082:unit-02 | 10commandments:chunk-0082 |
| 19 | 10commandments:chunk-0031:unit-02 | 10commandments:chunk-0031 |
| 20 | 10commandments:chunk-0013:unit-01 | 10commandments:chunk-0013 |

### paraphrased-03

Matched relevant parents: 10commandments:chunk-0059.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0066 |
| 2 | 10commandments:chunk-0057 |
| 3 | 10commandments:chunk-0059 |
| 4 | 10commandments:chunk-0067 |
| 5 | 10commandments:chunk-0048 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0066:unit-01 | 10commandments:chunk-0066 |
| 2 | 10commandments:chunk-0057:unit-02 | 10commandments:chunk-0057 |
| 3 | 10commandments:chunk-0059:unit-01 | 10commandments:chunk-0059 |
| 4 | 10commandments:chunk-0067:unit-01 | 10commandments:chunk-0067 |
| 5 | 10commandments:chunk-0048:unit-01 | 10commandments:chunk-0048 |
| 6 | 10commandments:chunk-0052:unit-01 | 10commandments:chunk-0052 |
| 7 | 10commandments:chunk-0068:unit-02 | 10commandments:chunk-0068 |
| 8 | 10commandments:chunk-0058:unit-01 | 10commandments:chunk-0058 |
| 9 | 10commandments:chunk-0065:unit-01 | 10commandments:chunk-0065 |
| 10 | 10commandments:chunk-0047:unit-02 | 10commandments:chunk-0047 |
| 11 | 10commandments:chunk-0065:unit-02 | 10commandments:chunk-0065 |
| 12 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 13 | 10commandments:chunk-0110:unit-01 | 10commandments:chunk-0110 |
| 14 | 10commandments:chunk-0053:unit-01 | 10commandments:chunk-0053 |
| 15 | 10commandments:chunk-0058:unit-02 | 10commandments:chunk-0058 |
| 16 | 10commandments:chunk-0054:unit-01 | 10commandments:chunk-0054 |
| 17 | 10commandments:chunk-0016:unit-02 | 10commandments:chunk-0016 |
| 18 | 10commandments:chunk-0107:unit-02 | 10commandments:chunk-0107 |
| 19 | 10commandments:chunk-0055:unit-01 | 10commandments:chunk-0055 |
| 20 | 10commandments:chunk-0057:unit-01 | 10commandments:chunk-0057 |

### paraphrased-04

Matched relevant parents: 10commandments:chunk-0063, 10commandments:chunk-0064.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0044 |
| 2 | 10commandments:chunk-0063 |
| 3 | 10commandments:chunk-0064 |
| 4 | 10commandments:chunk-0043 |
| 5 | 10commandments:chunk-0015 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0044:unit-01 | 10commandments:chunk-0044 |
| 2 | 10commandments:chunk-0063:unit-01 | 10commandments:chunk-0063 |
| 3 | 10commandments:chunk-0064:unit-01 | 10commandments:chunk-0064 |
| 4 | 10commandments:chunk-0043:unit-02 | 10commandments:chunk-0043 |
| 5 | 10commandments:chunk-0015:unit-01 | 10commandments:chunk-0015 |
| 6 | 10commandments:chunk-0075:unit-01 | 10commandments:chunk-0075 |
| 7 | 10commandments:chunk-0059:unit-01 | 10commandments:chunk-0059 |
| 8 | 10commandments:chunk-0062:unit-01 | 10commandments:chunk-0062 |
| 9 | 10commandments:chunk-0065:unit-02 | 10commandments:chunk-0065 |
| 10 | 10commandments:chunk-0061:unit-01 | 10commandments:chunk-0061 |
| 11 | 10commandments:chunk-0040:unit-01 | 10commandments:chunk-0040 |
| 12 | 10commandments:chunk-0014:unit-01 | 10commandments:chunk-0014 |
| 13 | 10commandments:chunk-0060:unit-01 | 10commandments:chunk-0060 |
| 14 | 10commandments:chunk-0096:unit-01 | 10commandments:chunk-0096 |
| 15 | 10commandments:chunk-0065:unit-01 | 10commandments:chunk-0065 |
| 16 | 10commandments:chunk-0041:unit-01 | 10commandments:chunk-0041 |
| 17 | 10commandments:chunk-0016:unit-02 | 10commandments:chunk-0016 |
| 18 | 10commandments:chunk-0084:unit-01 | 10commandments:chunk-0084 |
| 19 | 10commandments:chunk-0114:unit-01 | 10commandments:chunk-0114 |
| 20 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |

### paraphrased-05

Matched relevant parents: none.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0101 |
| 2 | 10commandments:chunk-0099 |
| 3 | 10commandments:chunk-0098 |
| 4 | 10commandments:chunk-0094 |
| 5 | 10commandments:chunk-0096 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0101:unit-01 | 10commandments:chunk-0101 |
| 2 | 10commandments:chunk-0099:unit-01 | 10commandments:chunk-0099 |
| 3 | 10commandments:chunk-0098:unit-02 | 10commandments:chunk-0098 |
| 4 | 10commandments:chunk-0094:unit-02 | 10commandments:chunk-0094 |
| 5 | 10commandments:chunk-0096:unit-01 | 10commandments:chunk-0096 |
| 6 | 10commandments:chunk-0081:unit-01 | 10commandments:chunk-0081 |
| 7 | 10commandments:chunk-0059:unit-01 | 10commandments:chunk-0059 |
| 8 | 10commandments:chunk-0104:unit-02 | 10commandments:chunk-0104 |
| 9 | 10commandments:chunk-0084:unit-01 | 10commandments:chunk-0084 |
| 10 | 10commandments:chunk-0102:unit-01 | 10commandments:chunk-0102 |
| 11 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 12 | 10commandments:chunk-0061:unit-01 | 10commandments:chunk-0061 |
| 13 | 10commandments:chunk-0065:unit-02 | 10commandments:chunk-0065 |
| 14 | 10commandments:chunk-0100:unit-02 | 10commandments:chunk-0100 |
| 15 | 10commandments:chunk-0080:unit-02 | 10commandments:chunk-0080 |
| 16 | 10commandments:chunk-0105:unit-01 | 10commandments:chunk-0105 |
| 17 | 10commandments:chunk-0097:unit-01 | 10commandments:chunk-0097 |
| 18 | 10commandments:chunk-0111:unit-01 | 10commandments:chunk-0111 |
| 19 | 10commandments:chunk-0092:unit-02 | 10commandments:chunk-0092 |
| 20 | 10commandments:chunk-0010:unit-01 | 10commandments:chunk-0010 |

### conceptual-01

Matched relevant parents: 10commandments:chunk-0002.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0005 |
| 2 | 10commandments:chunk-0007 |
| 3 | 10commandments:chunk-0106 |
| 4 | 10commandments:chunk-0002 |
| 5 | 10commandments:chunk-0006 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0005:unit-02 | 10commandments:chunk-0005 |
| 2 | 10commandments:chunk-0007:unit-01 | 10commandments:chunk-0007 |
| 3 | 10commandments:chunk-0106:unit-01 | 10commandments:chunk-0106 |
| 4 | 10commandments:chunk-0002:unit-01 | 10commandments:chunk-0002 |
| 5 | 10commandments:chunk-0006:unit-03 | 10commandments:chunk-0006 |
| 6 | 10commandments:chunk-0002:unit-02 | 10commandments:chunk-0002 |
| 7 | 10commandments:chunk-0001:unit-01 | 10commandments:chunk-0001 |
| 8 | 10commandments:chunk-0003:unit-02 | 10commandments:chunk-0003 |
| 9 | 10commandments:chunk-0111:unit-01 | 10commandments:chunk-0111 |
| 10 | 10commandments:chunk-0040:unit-01 | 10commandments:chunk-0040 |
| 11 | 10commandments:chunk-0005:unit-01 | 10commandments:chunk-0005 |
| 12 | 10commandments:chunk-0051:unit-01 | 10commandments:chunk-0051 |
| 13 | 10commandments:chunk-0013:unit-02 | 10commandments:chunk-0013 |
| 14 | 10commandments:chunk-0076:unit-01 | 10commandments:chunk-0076 |
| 15 | 10commandments:chunk-0110:unit-01 | 10commandments:chunk-0110 |
| 16 | 10commandments:chunk-0031:unit-02 | 10commandments:chunk-0031 |
| 17 | 10commandments:chunk-0032:unit-01 | 10commandments:chunk-0032 |
| 18 | 10commandments:chunk-0044:unit-01 | 10commandments:chunk-0044 |
| 19 | 10commandments:chunk-0008:unit-01 | 10commandments:chunk-0008 |
| 20 | 10commandments:chunk-0053:unit-01 | 10commandments:chunk-0053 |

### conceptual-02

Matched relevant parents: 10commandments:chunk-0106, 10commandments:chunk-0005.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0106 |
| 2 | 10commandments:chunk-0114 |
| 3 | 10commandments:chunk-0111 |
| 4 | 10commandments:chunk-0005 |
| 5 | 10commandments:chunk-0110 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0106:unit-01 | 10commandments:chunk-0106 |
| 2 | 10commandments:chunk-0114:unit-02 | 10commandments:chunk-0114 |
| 3 | 10commandments:chunk-0111:unit-01 | 10commandments:chunk-0111 |
| 4 | 10commandments:chunk-0005:unit-01 | 10commandments:chunk-0005 |
| 5 | 10commandments:chunk-0110:unit-01 | 10commandments:chunk-0110 |
| 6 | 10commandments:chunk-0114:unit-01 | 10commandments:chunk-0114 |
| 7 | 10commandments:chunk-0113:unit-01 | 10commandments:chunk-0113 |
| 8 | 10commandments:chunk-0108:unit-01 | 10commandments:chunk-0108 |
| 9 | 10commandments:chunk-0107:unit-02 | 10commandments:chunk-0107 |
| 10 | 10commandments:chunk-0109:unit-01 | 10commandments:chunk-0109 |
| 11 | 10commandments:chunk-0009:unit-01 | 10commandments:chunk-0009 |
| 12 | 10commandments:chunk-0112:unit-01 | 10commandments:chunk-0112 |
| 13 | 10commandments:chunk-0016:unit-02 | 10commandments:chunk-0016 |
| 14 | 10commandments:chunk-0106:unit-02 | 10commandments:chunk-0106 |
| 15 | 10commandments:chunk-0020:unit-01 | 10commandments:chunk-0020 |
| 16 | 10commandments:chunk-0013:unit-02 | 10commandments:chunk-0013 |
| 17 | 10commandments:chunk-0016:unit-01 | 10commandments:chunk-0016 |
| 18 | 10commandments:chunk-0115:unit-01 | 10commandments:chunk-0115 |
| 19 | 10commandments:chunk-0063:unit-01 | 10commandments:chunk-0063 |
| 20 | 10commandments:chunk-0013:unit-01 | 10commandments:chunk-0013 |

### conceptual-03

Matched relevant parents: 10commandments:chunk-0035, 10commandments:chunk-0034.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0035 |
| 2 | 10commandments:chunk-0033 |
| 3 | 10commandments:chunk-0034 |
| 4 | 10commandments:chunk-0032 |
| 5 | 10commandments:chunk-0021 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0035:unit-01 | 10commandments:chunk-0035 |
| 2 | 10commandments:chunk-0033:unit-01 | 10commandments:chunk-0033 |
| 3 | 10commandments:chunk-0034:unit-02 | 10commandments:chunk-0034 |
| 4 | 10commandments:chunk-0032:unit-01 | 10commandments:chunk-0032 |
| 5 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 6 | 10commandments:chunk-0038:unit-01 | 10commandments:chunk-0038 |
| 7 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 8 | 10commandments:chunk-0034:unit-01 | 10commandments:chunk-0034 |
| 9 | 10commandments:chunk-0037:unit-01 | 10commandments:chunk-0037 |
| 10 | 10commandments:chunk-0006:unit-03 | 10commandments:chunk-0006 |
| 11 | 10commandments:chunk-0039:unit-01 | 10commandments:chunk-0039 |
| 12 | 10commandments:chunk-0077:unit-01 | 10commandments:chunk-0077 |
| 13 | 10commandments:chunk-0107:unit-02 | 10commandments:chunk-0107 |
| 14 | 10commandments:chunk-0016:unit-02 | 10commandments:chunk-0016 |
| 15 | 10commandments:chunk-0059:unit-01 | 10commandments:chunk-0059 |
| 16 | 10commandments:chunk-0031:unit-02 | 10commandments:chunk-0031 |
| 17 | 10commandments:chunk-0039:unit-02 | 10commandments:chunk-0039 |
| 18 | 10commandments:chunk-0068:unit-01 | 10commandments:chunk-0068 |
| 19 | 10commandments:chunk-0067:unit-01 | 10commandments:chunk-0067 |
| 20 | 10commandments:chunk-0073:unit-01 | 10commandments:chunk-0073 |

### conceptual-04

Matched relevant parents: 10commandments:chunk-0013, 10commandments:chunk-0012.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0013 |
| 2 | 10commandments:chunk-0075 |
| 3 | 10commandments:chunk-0065 |
| 4 | 10commandments:chunk-0061 |
| 5 | 10commandments:chunk-0012 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0013:unit-01 | 10commandments:chunk-0013 |
| 2 | 10commandments:chunk-0075:unit-01 | 10commandments:chunk-0075 |
| 3 | 10commandments:chunk-0065:unit-02 | 10commandments:chunk-0065 |
| 4 | 10commandments:chunk-0061:unit-01 | 10commandments:chunk-0061 |
| 5 | 10commandments:chunk-0012:unit-01 | 10commandments:chunk-0012 |
| 6 | 10commandments:chunk-0059:unit-01 | 10commandments:chunk-0059 |
| 7 | 10commandments:chunk-0057:unit-01 | 10commandments:chunk-0057 |
| 8 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 9 | 10commandments:chunk-0087:unit-01 | 10commandments:chunk-0087 |
| 10 | 10commandments:chunk-0030:unit-01 | 10commandments:chunk-0030 |
| 11 | 10commandments:chunk-0084:unit-01 | 10commandments:chunk-0084 |
| 12 | 10commandments:chunk-0048:unit-01 | 10commandments:chunk-0048 |
| 13 | 10commandments:chunk-0053:unit-01 | 10commandments:chunk-0053 |
| 14 | 10commandments:chunk-0094:unit-01 | 10commandments:chunk-0094 |
| 15 | 10commandments:chunk-0093:unit-01 | 10commandments:chunk-0093 |
| 16 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 17 | 10commandments:chunk-0007:unit-01 | 10commandments:chunk-0007 |
| 18 | 10commandments:chunk-0016:unit-02 | 10commandments:chunk-0016 |
| 19 | 10commandments:chunk-0047:unit-01 | 10commandments:chunk-0047 |
| 20 | 10commandments:chunk-0086:unit-02 | 10commandments:chunk-0086 |

### conceptual-05

Matched relevant parents: 10commandments:chunk-0019.

| Parent rank | Parent chunk |
| --- | --- |
| 1 | 10commandments:chunk-0019 |
| 2 | 10commandments:chunk-0059 |
| 3 | 10commandments:chunk-0104 |
| 4 | 10commandments:chunk-0053 |
| 5 | 10commandments:chunk-0065 |

| Unit rank | Unit | Parent chunk |
| --- | --- | --- |
| 1 | 10commandments:chunk-0019:unit-01 | 10commandments:chunk-0019 |
| 2 | 10commandments:chunk-0059:unit-01 | 10commandments:chunk-0059 |
| 3 | 10commandments:chunk-0104:unit-03 | 10commandments:chunk-0104 |
| 4 | 10commandments:chunk-0053:unit-01 | 10commandments:chunk-0053 |
| 5 | 10commandments:chunk-0065:unit-02 | 10commandments:chunk-0065 |
| 6 | 10commandments:chunk-0048:unit-01 | 10commandments:chunk-0048 |
| 7 | 10commandments:chunk-0061:unit-01 | 10commandments:chunk-0061 |
| 8 | 10commandments:chunk-0101:unit-01 | 10commandments:chunk-0101 |
| 9 | 10commandments:chunk-0020:unit-01 | 10commandments:chunk-0020 |
| 10 | 10commandments:chunk-0021:unit-01 | 10commandments:chunk-0021 |
| 11 | 10commandments:chunk-0094:unit-01 | 10commandments:chunk-0094 |
| 12 | 10commandments:chunk-0099:unit-01 | 10commandments:chunk-0099 |
| 13 | 10commandments:chunk-0081:unit-01 | 10commandments:chunk-0081 |
| 14 | 10commandments:chunk-0096:unit-01 | 10commandments:chunk-0096 |
| 15 | 10commandments:chunk-0036:unit-01 | 10commandments:chunk-0036 |
| 16 | 10commandments:chunk-0084:unit-01 | 10commandments:chunk-0084 |
| 17 | 10commandments:chunk-0065:unit-01 | 10commandments:chunk-0065 |
| 18 | 10commandments:chunk-0010:unit-01 | 10commandments:chunk-0010 |
| 19 | 10commandments:chunk-0080:unit-02 | 10commandments:chunk-0080 |
| 20 | 10commandments:chunk-0094:unit-02 | 10commandments:chunk-0094 |

