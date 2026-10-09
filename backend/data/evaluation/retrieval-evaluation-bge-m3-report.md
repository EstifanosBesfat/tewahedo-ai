# BGE-M3 retrieval comparison

The controlled BGE-M3 run did not produce retrieval scores.

Stage: download

Error: `RuntimeError: could not download pytorch_model.bin`

E5 artifacts and ground-truth-v3 were not modified. No smaller model was substituted.

## Resource measurement

```json
{
  "system_memory_start": {
    "total_physical_gb": 7.804,
    "available_physical_gb": 0.697,
    "memory_load_percent": 91,
    "available_pagefile_gb": 5.733
  },
  "marks": {
    "before_download": {
      "elapsed_seconds": 0.039,
      "system": {
        "total_physical_gb": 7.804,
        "available_physical_gb": 0.684,
        "memory_load_percent": 91,
        "available_pagefile_gb": 5.723
      },
      "process": {
        "working_set_gb": 0.039,
        "peak_working_set_gb": 0.039,
        "pagefile_gb": 0.123,
        "peak_pagefile_gb": 0.123
      }
    }
  },
  "process_memory_end": {
    "working_set_gb": 0.026,
    "peak_working_set_gb": 0.054,
    "pagefile_gb": 0.142,
    "peak_pagefile_gb": 0.143
  }
}
```
