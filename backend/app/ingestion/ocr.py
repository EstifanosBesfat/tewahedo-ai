"""Amharic OCR for PDF pages rendered by PyMuPDF."""

from __future__ import annotations

import os
import shutil
import statistics
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image, ImageOps

OCR_DPI = 300
OCR_PSM = 3
OCR_LANGUAGE = "amh"
PREPROCESSING = "grayscale_autocontrast"
LOCAL_TESSDATA = Path(__file__).resolve().parents[2] / ".tessdata"


class OcrError(Exception):
    """Raised when Amharic OCR cannot process a page."""


@dataclass(frozen=True)
class OcrLine:
    text: str
    confidence: float
    left: int
    top: int
    right: int
    bottom: int


@dataclass(frozen=True)
class OcrResult:
    raw_text: str
    lines: tuple[OcrLine, ...]
    language: str
    dpi: int
    psm: int
    preprocessing: str
    image_width: int
    image_height: int
    mean_confidence: float | None


def _configure_tesseract() -> None:
    if shutil.which("tesseract"):
        return

    candidates = (
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(candidate)
            return


def _tessdata_config() -> str:
    if (LOCAL_TESSDATA / "amh.traineddata").is_file():
        os.environ["TESSDATA_PREFIX"] = str(LOCAL_TESSDATA)
    return ""


def _verify_languages(config: str) -> None:
    try:
        installed = set(pytesseract.get_languages(config=config))
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrError(
            "Tesseract OCR is not installed or cannot be found. "
            "Install Tesseract with the Amharic 'amh' language model."
        ) from exc

    if "amh" not in installed:
        raise OcrError(
            "Tesseract is installed, but its Amharic 'amh' language model "
            "is missing."
        )
def render_page(page: pymupdf.Page, dpi: int = OCR_DPI) -> Image.Image:
    """Render and gently normalize a scan without modifying the PDF."""
    pixmap = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, alpha=False)
    with Image.open(BytesIO(pixmap.tobytes("png"))) as image:
        grayscale = image.convert("L")
        return ImageOps.autocontrast(grayscale, cutoff=1)


def _lines_from_data(data: dict[str, list]) -> tuple[OcrLine, ...]:
    grouped: dict[tuple[int, int, int, int], list[int]] = {}
    for index, text in enumerate(data["text"]):
        if str(text).strip():
            key = (
                int(data["page_num"][index]),
                int(data["block_num"][index]),
                int(data["par_num"][index]),
                int(data["line_num"][index]),
            )
            grouped.setdefault(key, []).append(index)

    lines: list[OcrLine] = []
    for indexes in grouped.values():
        words = [str(data["text"][index]).strip() for index in indexes]
        confidences = [
            float(data["conf"][index])
            for index in indexes
            if float(data["conf"][index]) >= 0
        ]
        left = min(int(data["left"][index]) for index in indexes)
        top = min(int(data["top"][index]) for index in indexes)
        right = max(
            int(data["left"][index]) + int(data["width"][index])
            for index in indexes
        )
        bottom = max(
            int(data["top"][index]) + int(data["height"][index])
            for index in indexes
        )
        lines.append(
            OcrLine(
                text=" ".join(words),
                confidence=statistics.fmean(confidences) if confidences else 0.0,
                left=left,
                top=top,
                right=right,
                bottom=bottom,
            )
        )
    return tuple(sorted(lines, key=lambda line: (line.top, line.left)))


def _raw_text(lines: tuple[OcrLine, ...]) -> str:
    return "\n".join(line.text for line in lines).strip() + ("\n" if lines else "")


def ocr_page(page: pymupdf.Page) -> OcrResult:
    """Recognize an Amharic scan and retain confidence/position metadata."""
    _configure_tesseract()
    tessdata_config = _tessdata_config()
    _verify_languages(tessdata_config)
    image = render_page(page)
    try:
        data = pytesseract.image_to_data(
            image,
            lang=OCR_LANGUAGE,
            config=f"{tessdata_config} --oem 1 --psm {OCR_PSM}".strip(),
            output_type=pytesseract.Output.DICT,
        )
        lines = _lines_from_data(data)
        confidences = [line.confidence for line in lines if line.confidence >= 0]
        return OcrResult(
            raw_text=_raw_text(lines),
            lines=lines,
            language=OCR_LANGUAGE,
            dpi=OCR_DPI,
            psm=OCR_PSM,
            preprocessing=PREPROCESSING,
            image_width=image.width,
            image_height=image.height,
            mean_confidence=(
                statistics.fmean(confidences) if confidences else None
            ),
        )
    except pytesseract.TesseractError as exc:
        raise OcrError(f"Tesseract OCR failed: {exc}") from exc
    finally:
        image.close()
