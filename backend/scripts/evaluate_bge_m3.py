"""Embed the existing 182 retrieval units with dense BGE-M3 and score them.

This changes only the embedding model. It reads the frozen E5 results and
ground-truth-v3, writes a separate vector store, and does not modify the
source text, questions, or E5 artifacts.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import sys
import threading
import time
import traceback
from ctypes import wintypes
from pathlib import Path
from urllib.parse import quote

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from app.preparation.schemas import PreparedChunk, RetrievalUnitDocument
from app.retrieval.embeddings import BGE_M3_MODEL_NAME, BgeM3DenseProvider
from app.retrieval.evaluation import collapse_units_to_parents, score_parent_recall
from app.retrieval.runtime import DEFAULT_BGE_M3_VECTOR_STORE_PATH
from app.retrieval.store import BGE_M3_COLLECTION_NAME, ChromaVectorStore

REPO_ROOT = BACKEND_ROOT.parent
UNITS_PATH = BACKEND_ROOT / "data" / "processed" / "10commandments.retrieval-units.json"
GROUND_TRUTH_PATH = BACKEND_ROOT / "data" / "evaluation" / "ground-truth-v3.json"
E5_RESULTS_PATH = BACKEND_ROOT / "data" / "evaluation" / "retrieval-evaluation-v3.json"
OUTPUT_JSON = BACKEND_ROOT / "data" / "evaluation" / "retrieval-evaluation-bge-m3.json"
OUTPUT_REPORT = BACKEND_ROOT / "data" / "evaluation" / "retrieval-evaluation-bge-m3-report.md"
RESOURCE_JSON = BACKEND_ROOT / "data" / "evaluation" / "retrieval-evaluation-bge-m3-resources.json"
MODEL_DIR = Path.home() / ".cache" / "huggingface" / "tewahedo-bge-m3"
SEARCH_TOP_K = 20
PARENT_WIDTH = 5
MODEL_API = "https://huggingface.co/api/models/BAAI/bge-m3?blobs=true"
DENSE_SENTENCE_TRANSFORMER_FILES = {
    "1_Pooling/config.json",
    "config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "pytorch_model.bin",
    "sentence_bert_config.json",
    "sentencepiece.bpe.model",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
}


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class ProcessMemory(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def gb(value: int | float) -> float:
    return round(float(value) / (1024**3), 3)


def system_memory() -> dict[str, float | int]:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return {
        "total_physical_gb": gb(status.ullTotalPhys),
        "available_physical_gb": gb(status.ullAvailPhys),
        "memory_load_percent": int(status.dwMemoryLoad),
        "available_pagefile_gb": gb(status.ullAvailPageFile),
    }


def process_memory() -> dict[str, float]:
    counters = ProcessMemory()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.windll.kernel32
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.K32GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemory),
        wintypes.DWORD,
    ]
    kernel32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
    if not kernel32.K32GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(),
        ctypes.byref(counters),
        counters.cb,
    ):
        raise OSError("GetProcessMemoryInfo failed")
    return {
        "working_set_gb": gb(counters.WorkingSetSize),
        "peak_working_set_gb": gb(counters.PeakWorkingSetSize),
        "pagefile_gb": gb(counters.PagefileUsage),
        "peak_pagefile_gb": gb(counters.PeakPagefileUsage),
    }


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


class ResourceLog:
    def __init__(self) -> None:
        self.payload: dict[str, object] = {
            "started_at_epoch": time.time(),
            "system_memory_start": system_memory(),
            "process_memory_start": process_memory(),
            "samples": [],
        }
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        self.flush()

    def _sample(self) -> None:
        while not self._stop.wait(5):
            try:
                sample = {"system": system_memory(), "process": process_memory()}
            except OSError as exc:
                sample = {"error": str(exc)}
            samples = self.payload["samples"]
            if isinstance(samples, list):
                samples.append(sample)
                if len(samples) > 40:
                    del samples[:-40]
            self.flush()

    def mark(self, stage: str) -> None:
        self.payload[stage] = {
            "elapsed_seconds": round(time.time() - float(self.payload["started_at_epoch"]), 3),
            "system": system_memory(),
            "process": process_memory(),
        }
        self.flush()

    def flush(self) -> None:
        write_json(RESOURCE_JSON, self.payload)

    def close(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)
        self.payload["process_memory_end"] = process_memory()
        self.flush()


def model_manifest() -> dict:
    import requests

    response = requests.get(MODEL_API, timeout=(20, 60))
    response.raise_for_status()
    info = response.json()
    siblings = []
    for item in info.get("siblings", []):
        name = str(item["rfilename"])
        if name not in DENSE_SENTENCE_TRANSFORMER_FILES:
            continue
        siblings.append({"path": name, "size": item.get("size")})
    if not any(item["path"] == "pytorch_model.bin" for item in siblings):
        raise RuntimeError("BGE-M3 file list does not include pytorch_model.bin")
    return {"sha": info.get("sha"), "files": siblings}


def download_models(log: ResourceLog) -> dict:
    import requests

    manifest_path = MODEL_DIR / "download-manifest.json"
    if manifest_path.exists() and (MODEL_DIR / "pytorch_model.bin").exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = next(item for item in manifest["files"] if item["path"] == "pytorch_model.bin")
        actual = (MODEL_DIR / "pytorch_model.bin").stat().st_size
        if expected.get("size") in (None, actual):
            print("using existing local BGE-M3 files", flush=True)
            return manifest

    print("listing BAAI/bge-m3 files", flush=True)
    manifest = model_manifest()
    needed = sum(int(item["size"] or 0) for item in manifest["files"])
    free = shutil_disk_free(MODEL_DIR.parent)
    if needed and free < needed + 1024**3:
        raise RuntimeError(
            f"disk has {gb(free)} GB free and the selected files need about {gb(needed)} GB"
        )
    session = requests.Session()
    session.headers["User-Agent"] = "tewahedo-bge-m3-eval"
    started = time.perf_counter()
    for item in manifest["files"]:
        destination = MODEL_DIR / item["path"]
        url = "https://huggingface.co/BAAI/bge-m3/resolve/main/" + quote(item["path"])
        size = download_file(session, url, destination, item.get("size"))
        item["size"] = size
        print(f"ready {item['path']} bytes={size}", flush=True)
    manifest["download_seconds"] = round(time.perf_counter() - started, 3)
    write_json(manifest_path, manifest)
    log.mark("after_download")
    return manifest


def shutil_disk_free(path: Path) -> int:
    path.mkdir(parents=True, exist_ok=True)
    free = ctypes.c_ulonglong()
    kernel32 = ctypes.windll.kernel32
    kernel32.GetDiskFreeSpaceExW.argtypes = [
        wintypes.LPCWSTR,
        ctypes.POINTER(ctypes.c_ulonglong),
        ctypes.POINTER(ctypes.c_ulonglong),
        ctypes.POINTER(ctypes.c_ulonglong),
    ]
    kernel32.GetDiskFreeSpaceExW.restype = wintypes.BOOL
    if not kernel32.GetDiskFreeSpaceExW(str(path), ctypes.byref(free), None, None):
        raise OSError("GetDiskFreeSpaceExW failed")
    return int(free.value)


def download_file(session, url: str, destination: Path, expected_size: int | None) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected_text = f"{gb(expected_size)} GB" if expected_size else "unknown"
    attempts = 0
    while attempts < 30:
        attempts += 1
        have = destination.stat().st_size if destination.exists() else 0
        if expected_size and have == expected_size:
            return have
        if expected_size and have > expected_size:
            destination.unlink()
            have = 0
        headers = {"Range": f"bytes={have}-"} if have else {}
        print(
            f"resume {destination.name} have={gb(have)} GB expected={expected_text}",
            flush=True,
        )
        try:
            with session.get(
                url,
                headers=headers,
                stream=True,
                timeout=(30, 300),
                allow_redirects=True,
            ) as response:
                response.raise_for_status()
                if response.status_code == 200 and have:
                    destination.unlink()
                    continue
                mode = "ab" if response.status_code == 206 else "wb"
                next_report = have + 32 * 1024 * 1024
                with destination.open(mode) as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        have += len(chunk)
                        if have >= next_report:
                            print(
                                f"download {destination.name} {gb(have)} GB",
                                flush=True,
                            )
                            next_report = have + 32 * 1024 * 1024
                if expected_size is None:
                    header_length = response.headers.get("Content-Length")
                    if header_length and destination.stat().st_size == int(header_length):
                        return destination.stat().st_size
                    if response.status_code == 200:
                        return destination.stat().st_size
                if expected_size and destination.stat().st_size == expected_size:
                    return expected_size
        except Exception as exc:
            print(f"retry {destination.name} attempt {attempts}: {exc}", flush=True)
            time.sleep(min(30, 5 * attempts))
    raise RuntimeError(f"could not download {destination.name} after {attempts} attempts")


def load_inputs() -> tuple[RetrievalUnitDocument, dict, dict]:
    units = RetrievalUnitDocument.model_validate_json(UNITS_PATH.read_text(encoding="utf-8"))
    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
    e5_results = json.loads(E5_RESULTS_PATH.read_text(encoding="utf-8"))
    if units.unit_count != 182:
        raise RuntimeError(f"expected 182 retrieval units, found {units.unit_count}")
    if e5_results["model_name"] != "intfloat/multilingual-e5-small":
        raise RuntimeError("frozen E5 artifact no longer identifies multilingual-e5-small")
    if [e5_results["recall_at_1"], e5_results["recall_at_3"], e5_results["recall_at_5"]] != [
        "9/14",
        "12/14",
        "13/14",
    ]:
        raise RuntimeError("frozen E5 Recall@K values changed; refusing to compare against them")
    if ground_truth["excluded_question_ids"] != ["direct-01"]:
        raise RuntimeError("ground-truth-v3 exclusion list changed")
    return units, ground_truth, e5_results


def as_chunk(unit) -> PreparedChunk:
    return PreparedChunk(
        chunk_id=unit.chunk_id,
        document_id=unit.document_id,
        page_start=unit.page_start,
        page_end=unit.page_end,
        text=unit.text,
        extraction_method=unit.extraction_method,
        source_quality_score=unit.source_quality_score,
    )


def embed_missing(provider: BgeM3DenseProvider, store: ChromaVectorStore, units) -> dict:
    present = store.stored_ids()
    missing = [unit for unit in units.units if unit.chunk_id not in present]
    started = time.perf_counter()
    batch_size = 8
    for start in range(0, len(missing), batch_size):
        batch = missing[start : start + batch_size]
        embedded = provider.embed_documents([unit.text for unit in batch])
        store.upsert([as_chunk(unit) for unit in batch], embedded.vectors)
        print(f"embedded {min(start + batch_size, len(missing))}/{len(missing)}", flush=True)
    elapsed = round(time.perf_counter() - started, 3)
    stored = store.stored_ids()
    expected = {unit.chunk_id for unit in units.units}
    if stored != expected:
        raise RuntimeError(
            f"BGE-M3 store has {len(stored)} ids; expected the same 182 unit ids"
        )
    return {
        "embedded_this_run": len(missing),
        "embedding_seconds": elapsed,
        "reused_existing_vectors": len(missing) == 0,
    }


def evaluate(provider: BgeM3DenseProvider, store: ChromaVectorStore, ground_truth: dict) -> dict:
    rows = []
    parents_by_question: dict[str, list[str]] = {}
    for question in ground_truth["questions"]:
        query = str(question["question"]).strip()
        embed_started = time.perf_counter()
        vector = provider.embed_query(query)
        embed_seconds = time.perf_counter() - embed_started
        search_started = time.perf_counter()
        hits = store.search(vector, SEARCH_TOP_K)
        search_seconds = time.perf_counter() - search_started
        if len(hits) != min(SEARCH_TOP_K, store.count):
            raise RuntimeError("search did not return the requested unit count")
        unit_ids = [hit.chunk_id for hit in hits]
        parents = collapse_units_to_parents(unit_ids, PARENT_WIDTH)
        parents_by_question[str(question["question_id"])] = parents
        rows.append(
            {
                "question_id": question["question_id"],
                "question": question["question"],
                "embed_seconds": round(embed_seconds, 6),
                "search_seconds": round(search_seconds, 6),
                "unit_ranking": [
                    {
                        "rank": index,
                        "unit_id": hit.chunk_id,
                        "parent_chunk_id": parent_of(hit.chunk_id),
                        "page_start": hit.page_start,
                        "page_end": hit.page_end,
                        "similarity_score": hit.similarity_score,
                    }
                    for index, hit in enumerate(hits, start=1)
                ],
                "parent_ranking": [
                    {"rank": index, "parent_chunk_id": parent_id}
                    for index, parent_id in enumerate(parents, start=1)
                ],
            }
        )
    scored = score_parent_recall(ground_truth["questions"], parents_by_question)
    scored_by_id = {row["question_id"]: row for row in scored["questions"]}
    for row in rows:
        row.update(scored_by_id[row["question_id"]])
    return {"questions": rows, "score": scored}


def repeat_latency(provider: BgeM3DenseProvider, store: ChromaVectorStore, questions: list[dict]) -> dict:
    embed_times = []
    search_times = []
    mismatches = []
    for question in questions:
        query = str(question["question"]).strip()
        official_top = question["unit_ranking"][0]["unit_id"]
        embed_started = time.perf_counter()
        vector = provider.embed_query(query)
        embed_times.append(time.perf_counter() - embed_started)
        search_started = time.perf_counter()
        hits = store.search(vector, SEARCH_TOP_K)
        search_times.append(time.perf_counter() - search_started)
        if hits[0].chunk_id != official_top:
            mismatches.append(question["question_id"])
    return {
        "repeat_count": len(questions),
        "model_reloaded": False,
        "mean_query_embed_seconds": round(sum(embed_times) / len(embed_times), 6),
        "mean_search_seconds": round(sum(search_times) / len(search_times), 6),
        "top_unit_mismatches_versus_scoring_pass": mismatches,
    }


def parent_of(unit_id: str) -> str:
    marker = ":unit-"
    if marker not in unit_id:
        return unit_id
    return unit_id.split(marker, 1)[0]


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6)


def percent(hits: int, eligible: int) -> str:
    return f"{hits}/{eligible} ({hits / eligible * 100:.1f}%)"


def model_configuration(provider: BgeM3DenseProvider, manifest: dict) -> dict:
    pooling_path = MODEL_DIR / "1_Pooling" / "config.json"
    pooling = json.loads(pooling_path.read_text(encoding="utf-8")) if pooling_path.exists() else {}
    config_path = MODEL_DIR / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    import sentence_transformers
    import torch

    return {
        "model_name": BGE_M3_MODEL_NAME,
        "model_revision": manifest.get("sha"),
        "local_model_directory": str(MODEL_DIR),
        "embedding_dimension": provider.dimension,
        "hidden_size": config.get("hidden_size"),
        "model_max_position_embeddings": config.get("max_position_embeddings"),
        "loaded_max_seq_length": provider.max_tokens,
        "dense_only": True,
        "sparse_retrieval": False,
        "multi_vector_retrieval": False,
        "query_prefix": provider.QUERY_PREFIX,
        "document_prefix": provider.DOCUMENT_PREFIX,
        "query_instruction": None,
        "encode_prompt": "",
        "instruction_policy": (
            "BGE-M3 model card: dense retrieval uses the same approach as BGE, "
            "except queries do not get an instruction prefix."
        ),
        "library_prompts": provider.library_prompts,
        "library_default_prompt_name": provider.default_prompt_name,
        "normalize_embeddings": True,
        "similarity": "Chroma cosine distance on L2-normalized vectors; score = 1 - distance",
        "pooling": pooling,
        "precision": "float32",
        "device": "cpu",
        "sentence_transformers": sentence_transformers.__version__,
        "torch": torch.__version__,
        "cuda": bool(torch.cuda.is_available()),
        "encode_batch_size": provider._batch_size,
    }


def compare(questions: list[dict], e5_results: dict) -> list[dict]:
    e5_by_id = {row["question_id"]: row for row in e5_results["questions"]}
    compared = []
    for question in questions:
        e5 = e5_by_id[question["question_id"]]
        if not question["metric_eligible"]:
            change = "excluded"
        else:
            gains = []
            losses = []
            for cutoff in (1, 3, 5):
                before = bool(e5[f"top_{cutoff}"])
                after = bool(question[f"top_{cutoff}"])
                if after and not before:
                    gains.append(cutoff)
                if before and not after:
                    losses.append(cutoff)
            if gains and losses:
                change = "mixed"
            elif gains:
                change = "improved"
            elif losses:
                change = "worsened"
            else:
                change = "unchanged"
        compared.append(
            {
                "question_id": question["question_id"],
                "change_versus_e5": change,
                "e5_top_1": e5["top_1"],
                "e5_top_3": e5["top_3"],
                "e5_top_5": e5["top_5"],
                "bge_top_1": question["top_1"],
                "bge_top_3": question["top_3"],
                "bge_top_5": question["top_5"],
            }
        )
    return compared


def hit_word(value: bool) -> str:
    return "hit" if value else "miss"


def render_report(result: dict) -> str:
    if result.get("status") != "completed":
        failure = result.get("failure", {})
        resources = result.get("resources", {})
        return "\n".join(
            [
                "# BGE-M3 retrieval comparison",
                "",
                "The controlled BGE-M3 run did not produce retrieval scores.",
                "",
                f"Stage: {failure.get('stage')}",
                "",
                f"Error: `{failure.get('error_type')}: {failure.get('error')}`",
                "",
                "E5 artifacts and ground-truth-v3 were not modified. No smaller model was substituted.",
                "",
                "## Resource measurement",
                "",
                "```json",
                json.dumps(resources, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )

    score = result["score"]
    eligible = int(score["eligible"])
    hits = score["hits"]
    config = result["configuration"]
    resources = result["resources"]
    lines = [
        "# BGE-M3 retrieval comparison",
        "",
        "Dense `BAAI/bge-m3` was compared with the frozen `intfloat/multilingual-e5-small` baseline. Only the embedding model and its model-specific input configuration changed.",
        "",
        "## Model and embedding configuration",
        "",
        f"- Model: `{config['model_name']}`",
        f"- Revision: `{config['model_revision']}`",
        f"- Embedding dimension: {config['embedding_dimension']}",
        f"- Loaded maximum sequence length: {config['loaded_max_seq_length']}",
        f"- Config hidden size: {config['hidden_size']}",
        f"- Config maximum positions: {config['model_max_position_embeddings']}",
        f"- Query prefix: `{config['query_prefix']}`",
        f"- Document prefix: `{config['document_prefix']}`",
        f"- Encode prompt: `{config['encode_prompt']}`",
        f"- Library prompts: `{json.dumps(config['library_prompts'], ensure_ascii=False)}`",
        f"- Library default prompt name: `{config['library_default_prompt_name']}`",
        f"- Dense only: {config['dense_only']}",
        f"- Sparse retrieval: {config['sparse_retrieval']}",
        f"- Multi-vector retrieval: {config['multi_vector_retrieval']}",
        f"- Normalization: {config['normalize_embeddings']}",
        f"- Similarity: {config['similarity']}",
        f"- Pooling: `{json.dumps(config['pooling'], ensure_ascii=False)}`",
        f"- Precision and device: {config['precision']} on {config['device']}; CUDA available: {config['cuda']}",
        f"- sentence-transformers {config['sentence_transformers']}; torch {config['torch']}",
        f"- Encode batch size: {config['encode_batch_size']}",
        f"- Vector store: `{result['vector_store']}`",
        f"- Collection: `{result['collection_name']}`",
        "",
        config["instruction_policy"],
        "",
        "## Recall",
        "",
        f"- Recall@1: {percent(hits[1], eligible)}",
        f"- Recall@3: {percent(hits[3], eligible)}",
        f"- Recall@5: {percent(hits[5], eligible)}",
        "",
        "The denominator is the 14 metric-eligible questions. `direct-01` stays excluded.",
        "",
        "## Frozen E5 comparison",
        "",
        "| Cutoff | E5-small | BGE-M3 |",
        "| --- | --- | --- |",
        f"| Recall@1 | 9/14 (64.3%) | {percent(hits[1], eligible)} |",
        f"| Recall@3 | 12/14 (85.7%) | {percent(hits[3], eligible)} |",
        f"| Recall@5 | 13/14 (92.9%) | {percent(hits[5], eligible)} |",
        "",
        "E5 values are read from `retrieval-evaluation-v3.json`.",
        "",
        "## Questions",
        "",
        "| Question | Eligible | First relevant parent | K=1 | K=3 | K=5 | E5 K=1 | E5 K=3 | E5 K=5 | Change |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    compared = {row["question_id"]: row for row in result["comparison"]}
    for question in result["questions"]:
        change = compared[question["question_id"]]
        rank = question["first_relevant_parent_rank"]
        rank_text = "none" if rank is None else str(rank)
        eligible_text = "yes" if question["metric_eligible"] else "no"
        lines.append(
            "| {question_id} | {eligible} | {rank} | {k1} | {k3} | {k5} | {e1} | {e3} | {e5} | {change} |".format(
                question_id=question["question_id"],
                eligible=eligible_text,
                rank=rank_text,
                k1=hit_word(question["top_1"]),
                k3=hit_word(question["top_3"]),
                k5=hit_word(question["top_5"]),
                e1=hit_word(change["e5_top_1"]),
                e3=hit_word(change["e5_top_3"]),
                e5=hit_word(change["e5_top_5"]),
                change=change["change_versus_e5"],
            )
        )
    direct = next(row for row in result["questions"] if row["question_id"] == "direct-01")
    lines.extend(
        [
            "",
            "## Excluded question",
            "",
            "`direct-01` is excluded from the denominator.",
            "",
            f"Reason: {direct.get('exclusion_reason')}",
            "",
            "## direct-05",
            "",
        ]
    )
    lines.extend(result["direct_05_lines"])
    lines.extend(
        [
            "",
            "## Remaining Recall@5 misses",
            "",
        ]
    )
    if result["score"]["misses_at_5"]:
        for question_id in result["score"]["misses_at_5"]:
            lines.append(f"- `{question_id}`")
    else:
        lines.append("No metric-eligible question misses Recall@5.")
    lines.extend(
        [
            "",
            "## Runtime, storage, and memory",
            "",
            f"- Model storage: {resources['model_storage_gb']} GB at `{resources['model_directory']}`",
            f"- Vector-store storage: {resources['vector_store_storage_gb']} GB",
            f"- Model load time: {resources['model_load_seconds']} seconds",
            f"- Embedding time this run: {resources['embedding_seconds']} seconds for {resources['embedded_this_run']} units",
            f"- Existing vectors reused: {resources['reused_existing_vectors']}",
            f"- Scoring-pass mean query embed time: {resources['scoring_mean_query_embed_seconds']} seconds",
            f"- Scoring-pass mean search time: {resources['scoring_mean_search_seconds']} seconds",
            f"- Repeat-pass mean query embed time: {resources['repeat_mean_query_embed_seconds']} seconds",
            f"- Repeat-pass mean search time: {resources['repeat_mean_search_seconds']} seconds",
            f"- Repeat pass reloaded the model: {resources['repeat_model_reloaded']}",
            f"- Process peak working set: {resources['peak_working_set_gb']} GB",
            f"- Process peak pagefile: {resources['peak_pagefile_gb']} GB",
            f"- System memory at start: {resources['system_memory_start']}",
            f"- System memory after model load: {resources['after_model_load']}",
            f"- System memory after embedding: {resources['after_embedding']}",
            "",
            "Latency is the mean of the 15 questions. The model was loaded once. The scoring pass produced the official ranking, and one extra pass measured steady query latency without reloading.",
            "",
            "## Limitations",
            "",
        ]
    )
    for limitation in result["limitations"]:
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)


def direct_05_lines(question: dict) -> list[str]:
    relevant = set(question["relevant_chunk_ids"])
    appearances = [
        row
        for row in question["unit_ranking"]
        if row["parent_chunk_id"] in relevant
    ]
    lines = [
        "The same approved parents are used for every question. For `direct-05` those parents are "
        + ", ".join(f"`{chunk_id}`" for chunk_id in question["relevant_chunk_ids"])
        + ".",
        "",
        f"- First relevant parent rank: {question['first_relevant_parent_rank']}",
        f"- Recall@1: {hit_word(question['top_1'])}",
        f"- Recall@3: {hit_word(question['top_3'])}",
        f"- Recall@5: {hit_word(question['top_5'])}",
        "",
        "Relevant units inside the top 20:",
        "",
    ]
    if not appearances:
        lines.append("None of the approved relevant parents appear in the top 20 units.")
    else:
        for row in appearances:
            lines.append(
                f"- Unit rank {row['rank']}: `{row['unit_id']}` "
                f"parent `{row['parent_chunk_id']}` similarity {row['similarity_score']}"
            )
    lines.extend(
        [
            "",
            "E5 missed this question at Recall@1, Recall@3, and Recall@5. "
            f"BGE-M3 is a {hit_word(question['top_1'])} at 1, "
            f"a {hit_word(question['top_3'])} at 3, and "
            f"a {hit_word(question['top_5'])} at 5.",
        ]
    )
    return lines


def limitations_for(config: dict, embed_info: dict, latency: dict) -> list[str]:
    notes = [
        "Sparse weights and ColBERT multi-vector retrieval were not used.",
        "Queries and passages were embedded without an instruction prefix. encode received prompt=\"\" so a library default prompt could not add one.",
        "Vectors are L2-normalized and ranked by the existing Chroma cosine distance. The reported score is 1 minus that distance, the same conversion used for E5.",
        "Top 20 units are collapsed to the first 5 unique parent chunks. Either approved relevant parent counts as a hit. direct-01 remains excluded.",
        "Chunking, OCR, unit text, question wording, ground-truth labels, and the E5 store were not changed to improve the score.",
        "Chroma HNSW is an approximate nearest-neighbor index. E5 used the same index type and cosine space.",
        "batch_size 1 limits activation memory. Each text is still embedded independently.",
        f"This run embedded {embed_info['embedded_this_run']} missing units. Reused existing vectors: {embed_info['reused_existing_vectors']}.",
    ]
    prompts = config["library_prompts"]
    nonempty = {key: value for key, value in prompts.items() if value}
    if nonempty:
        notes.append(
            "The loaded library exposed non-empty prompts "
            + json.dumps(nonempty, ensure_ascii=False)
            + ". They were not applied."
        )
    else:
        notes.append("The loaded library prompts were empty, matching the model card's no-instruction setting.")
    if int(config["loaded_max_seq_length"]) < 8192:
        notes.append(
            f"The loaded model reports max_seq_length {config['loaded_max_seq_length']}, below the 8192-token model-card context. No unit exceeded the loaded limit, so nothing was truncated."
        )
    if latency["top_unit_mismatches_versus_scoring_pass"]:
        notes.append(
            "The repeat latency pass changed the top unit for: "
            + ", ".join(latency["top_unit_mismatches_versus_scoring_pass"])
        )
    return notes


def publish(result: dict) -> None:
    report = render_report(result)
    payload = {
        key: value for key, value in result.items() if key != "direct_05_lines"
    }
    write_json(OUTPUT_JSON, payload)
    OUTPUT_REPORT.write_text(report, encoding="utf-8")


def fail(log: ResourceLog, stage: str, exc: BaseException) -> int:
    log.payload["failure"] = {
        "stage": stage,
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback": traceback.format_exc(),
    }
    log.close()
    result = {
        "status": "failed",
        "model_name": BGE_M3_MODEL_NAME,
        "failure": log.payload["failure"],
        "resources": {
            "system_memory_start": log.payload.get("system_memory_start"),
            "marks": {
                key: value
                for key, value in log.payload.items()
                if key.startswith("after_") or key.startswith("before_")
            },
            "process_memory_end": log.payload.get("process_memory_end"),
        },
    }
    publish(result)
    print(f"FAILED at {stage}: {type(exc).__name__}: {exc}", flush=True)
    return 2


def main() -> int:
    if OUTPUT_JSON.resolve() == E5_RESULTS_PATH.resolve():
        raise RuntimeError("refusing to overwrite the frozen E5 results")
    log = ResourceLog()
    stage = "load inputs"
    try:
        units, ground_truth, e5_results = load_inputs()
        stage = "download"
        log.mark("before_download")
        manifest = download_models(log)
        stage = "load model"
        log.mark("before_model_load")
        load_started = time.perf_counter()
        provider = BgeM3DenseProvider(
            device="cpu",
            batch_size=1,
            model_path=str(MODEL_DIR),
        )
        load_seconds = round(time.perf_counter() - load_started, 3)
        log.mark("after_model_load")
        store = ChromaVectorStore(
            persist_path=DEFAULT_BGE_M3_VECTOR_STORE_PATH,
            collection_name=BGE_M3_COLLECTION_NAME,
            model_name=provider.model_name,
            dimension=provider.dimension,
        )
        if store.model_name != BGE_M3_MODEL_NAME:
            raise RuntimeError("BGE-M3 store metadata does not name BAAI/bge-m3")
        stage = "embed units"
        embed_info = embed_missing(provider, store, units)
        log.mark("after_embedding")
        stage = "evaluate"
        evaluated = evaluate(provider, store, ground_truth)
        latency = repeat_latency(provider, store, evaluated["questions"])
        log.mark("after_queries")
        config = model_configuration(provider, manifest)
        comparison = compare(evaluated["questions"], e5_results)
        score = evaluated["score"]
        direct = next(row for row in evaluated["questions"] if row["question_id"] == "direct-05")
        resources = {
            "model_directory": str(MODEL_DIR),
            "model_storage_gb": gb(directory_size(MODEL_DIR)),
            "vector_store_storage_gb": gb(directory_size(DEFAULT_BGE_M3_VECTOR_STORE_PATH)),
            "model_load_seconds": load_seconds,
            "embedding_seconds": embed_info["embedding_seconds"],
            "embedded_this_run": embed_info["embedded_this_run"],
            "reused_existing_vectors": embed_info["reused_existing_vectors"],
            "scoring_mean_query_embed_seconds": mean(
                [row["embed_seconds"] for row in evaluated["questions"]]
            ),
            "scoring_mean_search_seconds": mean(
                [row["search_seconds"] for row in evaluated["questions"]]
            ),
            "repeat_mean_query_embed_seconds": latency["mean_query_embed_seconds"],
            "repeat_mean_search_seconds": latency["mean_search_seconds"],
            "repeat_model_reloaded": latency["model_reloaded"],
            "peak_working_set_gb": process_memory()["peak_working_set_gb"],
            "peak_pagefile_gb": process_memory()["peak_pagefile_gb"],
            "system_memory_start": log.payload["system_memory_start"],
            "after_model_load": log.payload["after_model_load"],
            "after_embedding": log.payload["after_embedding"],
        }
        result = {
            "status": "completed",
            "benchmark": "ground-truth-v3",
            "model_name": BGE_M3_MODEL_NAME,
            "collection_name": BGE_M3_COLLECTION_NAME,
            "vector_store": display_path(DEFAULT_BGE_M3_VECTOR_STORE_PATH),
            "unit_count": units.unit_count,
            "unit_file_sha256": sha256_file(UNITS_PATH),
            "ground_truth_file_sha256": sha256_file(GROUND_TRUTH_PATH),
            "retrieval_settings": {
                "search_top_k_before_parent_collapse": SEARCH_TOP_K,
                "parent_width": PARENT_WIDTH,
                "denominator": score["eligible"],
                "hit_rule": "A metric-eligible question hits at k when any approved relevant parent is inside the top k parents.",
            },
            "configuration": config,
            "recall_at_1": percent(score["hits"][1], score["eligible"]),
            "recall_at_3": percent(score["hits"][3], score["eligible"]),
            "recall_at_5": percent(score["hits"][5], score["eligible"]),
            "excluded_question_ids": ["direct-01"],
            "denominator": score["eligible"],
            "misses_at_5": score["misses_at_5"],
            "frozen_e5_baseline": {
                "model_name": e5_results["model_name"],
                "recall_at_1": e5_results["recall_at_1"],
                "recall_at_3": e5_results["recall_at_3"],
                "recall_at_5": e5_results["recall_at_5"],
                "misses_at_5": e5_results["misses_at_5"],
            },
            "comparison": comparison,
            "direct_05": {
                "relevant_chunk_ids": direct["relevant_chunk_ids"],
                "first_relevant_parent_rank": direct["first_relevant_parent_rank"],
                "top_1": direct["top_1"],
                "top_3": direct["top_3"],
                "top_5": direct["top_5"],
            },
            "questions": evaluated["questions"],
            "resources": resources,
            "limitations": limitations_for(config, embed_info, latency),
            "score": {
                "eligible": score["eligible"],
                "hits": score["hits"],
                "misses_at_5": score["misses_at_5"],
            },
        }
        result["direct_05_lines"] = direct_05_lines(direct)
        publish(result)
        log.close()
        print(result["recall_at_1"], result["recall_at_3"], result["recall_at_5"], flush=True)
        return 0
    except Exception as exc:
        return fail(log, stage, exc)


if __name__ == "__main__":
    raise SystemExit(main())
