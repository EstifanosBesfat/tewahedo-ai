# BGE-M3 retrieval comparison

Dense `BAAI/bge-m3` was compared with the frozen `intfloat/multilingual-e5-small` baseline. Only the embedding model and its model-specific input configuration changed.

## Model and embedding configuration

- Model: `BAAI/bge-m3`
- Revision: `5617a9f61b028005a4858fdac845db406aefb181`
- Embedding dimension: 1024
- Loaded maximum sequence length: 8192
- Config hidden size: 1024
- Config maximum positions: 8194
- Query prefix: ``
- Document prefix: ``
- Encode prompt: ``
- Library prompts: `{"query": "", "document": ""}`
- Library default prompt name: `None`
- Dense only: True
- Sparse retrieval: False
- Multi-vector retrieval: False
- Normalization: True
- Similarity: Chroma cosine distance on L2-normalized vectors; score = 1 - distance
- Pooling: `{"word_embedding_dimension": 1024, "pooling_mode_cls_token": true, "pooling_mode_mean_tokens": false, "pooling_mode_max_tokens": false, "pooling_mode_mean_sqrt_len_tokens": false}`
- Precision and device: float32 on cpu; CUDA available: False
- sentence-transformers 6.1.0; torch 2.14.1+cpu
- Encode batch size: 1
- Vector store: `backend/data/vectorstore/bge-m3-units`
- Collection: `tewahedo_bge_m3_dense_v1`

BGE-M3 model card: dense retrieval uses the same approach as BGE, except queries do not get an instruction prefix.

## Recall

- Recall@1: 12/14 (85.7%)
- Recall@3: 14/14 (100.0%)
- Recall@5: 14/14 (100.0%)

The denominator is the 14 metric-eligible questions. `direct-01` stays excluded.

## Frozen E5 comparison

| Cutoff | E5-small | BGE-M3 |
| --- | --- | --- |
| Recall@1 | 9/14 (64.3%) | 12/14 (85.7%) |
| Recall@3 | 12/14 (85.7%) | 14/14 (100.0%) |
| Recall@5 | 13/14 (92.9%) | 14/14 (100.0%) |

E5 values are read from `retrieval-evaluation-v3.json`.

## Questions

| Question | Eligible | First relevant parent | K=1 | K=3 | K=5 | E5 K=1 | E5 K=3 | E5 K=5 | Change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| direct-01 | no | none | miss | miss | miss | miss | miss | miss | excluded |
| direct-02 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| direct-03 | yes | 1 | hit | hit | hit | miss | hit | hit | improved |
| direct-04 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| direct-05 | yes | 2 | miss | hit | hit | miss | miss | miss | improved |
| paraphrased-01 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| paraphrased-02 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| paraphrased-03 | yes | 3 | miss | hit | hit | miss | hit | hit | unchanged |
| paraphrased-04 | yes | 1 | hit | hit | hit | miss | hit | hit | improved |
| paraphrased-05 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| conceptual-01 | yes | 1 | hit | hit | hit | miss | miss | hit | improved |
| conceptual-02 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| conceptual-03 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| conceptual-04 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |
| conceptual-05 | yes | 1 | hit | hit | hit | hit | hit | hit | unchanged |

## Excluded question

`direct-01` is excluded from the denominator.

Reason: The Amharic uses 'the first commandment' for three teachings. No one of them is the only concept the source states.

## direct-05

The same approved parents are used for every question. For `direct-05` those parents are `10commandments:chunk-0085`, `10commandments:chunk-0089`.

- First relevant parent rank: 2
- Recall@1: miss
- Recall@3: hit
- Recall@5: hit

Relevant units inside the top 20:

- Unit rank 2: `10commandments:chunk-0089:unit-02` parent `10commandments:chunk-0089` similarity 0.5300325155258179
- Unit rank 3: `10commandments:chunk-0089:unit-01` parent `10commandments:chunk-0089` similarity 0.5239508748054504
- Unit rank 7: `10commandments:chunk-0085:unit-01` parent `10commandments:chunk-0085` similarity 0.5106790065765381
- Unit rank 14: `10commandments:chunk-0085:unit-02` parent `10commandments:chunk-0085` similarity 0.4926949739456177

E5 missed this question at Recall@1, Recall@3, and Recall@5. BGE-M3 is a miss at 1, a hit at 3, and a hit at 5.

## Remaining Recall@5 misses

No metric-eligible question misses Recall@5.

## Runtime, storage, and memory

- Model storage: 2.136 GB at `C:\Users\estifanos besfat\.cache\huggingface\tewahedo-bge-m3`
- Vector-store storage: 0.003 GB
- Model load time: 110.199 seconds
- Embedding time this run: 958.816 seconds for 182 units
- Existing vectors reused: False
- Scoring-pass mean query embed time: 0.618295 seconds
- Scoring-pass mean search time: 0.049849 seconds
- Repeat-pass mean query embed time: 0.446476 seconds
- Repeat-pass mean search time: 0.006581 seconds
- Repeat pass reloaded the model: False
- Process peak working set: 1.239 GB
- Process peak pagefile: 3.152 GB
- System memory at start: {'total_physical_gb': 7.804, 'available_physical_gb': 0.318, 'memory_load_percent': 95, 'available_pagefile_gb': 4.174}
- System memory after model load: {'elapsed_seconds': 835.141, 'system': {'total_physical_gb': 7.804, 'available_physical_gb': 0.5, 'memory_load_percent': 93, 'available_pagefile_gb': 0.719}, 'process': {'working_set_gb': 0.626, 'peak_working_set_gb': 0.673, 'pagefile_gb': 3.023, 'peak_pagefile_gb': 3.068}}
- System memory after embedding: {'elapsed_seconds': 1801.935, 'system': {'total_physical_gb': 7.804, 'available_physical_gb': 0.762, 'memory_load_percent': 90, 'available_pagefile_gb': 1.239}, 'process': {'working_set_gb': 1.216, 'peak_working_set_gb': 1.239, 'pagefile_gb': 3.116, 'peak_pagefile_gb': 3.152}}

Latency is the mean of the 15 questions. The model was loaded once. The scoring pass produced the official ranking, and one extra pass measured steady query latency without reloading.

## Limitations

- Sparse weights and ColBERT multi-vector retrieval were not used.
- Queries and passages were embedded without an instruction prefix. encode received prompt="" so a library default prompt could not add one.
- Vectors are L2-normalized and ranked by the existing Chroma cosine distance. The reported score is 1 minus that distance, the same conversion used for E5.
- Top 20 units are collapsed to the first 5 unique parent chunks. Either approved relevant parent counts as a hit. direct-01 remains excluded.
- Chunking, OCR, unit text, question wording, ground-truth labels, and the E5 store were not changed to improve the score.
- Chroma HNSW is an approximate nearest-neighbor index. E5 used the same index type and cosine space.
- batch_size 1 limits activation memory. Each text is still embedded independently.
- This run embedded 182 missing units. Reused existing vectors: False.
- The loaded library prompts were empty, matching the model card's no-instruction setting.
- The published BGE-M3 snapshot uses `pytorch_model.bin` (2,271,145,830 bytes), not `model.safetensors`. The download needed ranged resume across dropped Hugging Face connections.
- The 7.8 GB machine ran the model by paging: after load the process pagefile was about 3.0 GB while the working set stayed under 1.3 GB. Available pagefile fell to 0.719 GB.
