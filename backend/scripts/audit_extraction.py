"""Re-extract PDFs and write a reproducible ingestion quality report."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.extractor import extracted_dir, ingest_pdf, raw_dir
from app.ingestion.schemas import ExtractedDocument
from app.ingestion.similarity import compare_documents


def _load_previous_text(path: Path) -> dict[int, str]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        int(page["page_number"]): str(page["text"])
        for page in payload.get("pages", [])
    }


def _excerpt(text: str, limit: int = 500) -> str:
    compact = "\n".join(line for line in text.splitlines() if line.strip())
    return compact[:limit]


def _document_statistics(document: ExtractedDocument) -> dict[str, object]:
    flags = Counter(
        flag for page in document.pages for flag in page.quality.flags
    )
    scores = [page.quality.score for page in document.pages]
    return {
        "filename": document.filename,
        "total_pages": document.page_count,
        "pymupdf_pages": sum(
            page.extraction_method == "pymupdf" for page in document.pages
        ),
        "ocr_pages": sum(
            page.extraction_method == "ocr" for page in document.pages
        ),
        "average_quality_score": (
            round(sum(scores) / len(scores), 2) if scores else 0.0
        ),
        "minimum_quality_score": min(scores) if scores else 0.0,
        "maximum_quality_score": max(scores) if scores else 0.0,
        "review_pages": [
            page.page_number
            for page in document.pages
            if "review_recommended" in page.quality.flags
        ],
        "flag_counts": dict(sorted(flags.items())),
        "page_quality": [
            {
                "page_number": page.page_number,
                "score": page.quality.score,
                "mean_confidence": page.quality.mean_confidence,
                "ethiopic_ratio": page.quality.ethiopic_ratio,
                "latin_ratio": page.quality.latin_ratio,
                "visible_characters": page.quality.visible_characters,
                "flags": page.quality.flags,
            }
            for page in document.pages
        ],
    }


def _before_after_examples(
    document: ExtractedDocument,
    previous: dict[int, str],
    count: int = 3,
) -> list[dict[str, object]]:
    candidates = []
    for page in document.pages:
        before = previous.get(page.page_number, page.raw_text)
        ratio = SequenceMatcher(None, before, page.text).ratio()
        candidates.append((ratio, page, before))
    return [
        {
            "page_number": page.page_number,
            "similarity_to_previous": round(ratio, 4),
            "before": _excerpt(before),
            "after": _excerpt(page.text),
            "removed_fragments": page.removed_fragments[:10],
            "quality_score": page.quality.score,
            "flags": page.quality.flags,
        }
        for ratio, page, before in sorted(candidates, key=lambda item: item[0])[
            :count
        ]
    ]


def run(filenames: list[str]) -> Path:
    source_directory = raw_dir()
    output_directory = extracted_dir()
    report_path = output_directory / "ingestion-quality-report.json"
    preserved_examples: dict[int, str] = {}
    if report_path.is_file():
        existing_report = json.loads(report_path.read_text(encoding="utf-8"))
        preserved_examples = {
            int(example["page_number"]): str(example["before"])
            for example in existing_report.get("before_after_examples", [])
        }
    previous = {
        filename: _load_previous_text(
            output_directory / Path(filename).with_suffix(".json")
        )
        for filename in filenames
    }
    documents: dict[str, ExtractedDocument] = {}
    for filename in filenames:
        document, _ = ingest_pdf(filename, source_directory, output_directory)
        documents[filename] = document

    report: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "direct_extraction": "PyMuPDF page text when usable",
            "ocr": "Tesseract amh, OEM 1, PSM 3, 300 DPI",
            "preprocessing": "grayscale with 1% autocontrast",
            "cleanup": (
                "repeated positional margins, website boilerplate, isolated "
                "Latin artifacts, and geometry-supported line wraps"
            ),
            "raw_ocr_preserved": True,
        },
        "documents": [
            _document_statistics(documents[filename]) for filename in filenames
        ],
    }

    longest = max(documents.values(), key=lambda document: document.page_count)
    previous[longest.filename].update(preserved_examples)
    report["before_after_examples"] = _before_after_examples(
        longest, previous[longest.filename]
    )
    if len(filenames) == 2:
        first_name, second_name = filenames
        first = documents[first_name]
        second = documents[second_name]
        comparison = compare_documents(
            source_directory / first_name,
            source_directory / second_name,
            "\n".join(page.text for page in first.pages),
            "\n".join(page.text for page in second.pages),
        )
        report["duplicate_analysis"] = comparison.to_dict()

    destination = report_path
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Re-extract raw PDFs and generate a quality audit."
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        default=["10commandments.pdf", "meron.pdf"],
    )
    args = parser.parse_args(argv)
    destination = run(args.filenames)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
