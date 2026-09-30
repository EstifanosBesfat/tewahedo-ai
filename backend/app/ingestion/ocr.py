"""Amharic OCR for PDF pages rendered by PyMuPDF."""

from __future__ import annotations

import os
import shutil
from io import BytesIO
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

OCR_DPI = 300
LOCAL_TESSDATA = Path(__file__).resolve().parents[2] / ".tessdata"


class OcrError(Exception):
    """Raised when Amharic OCR cannot process a page."""


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


def _verify_languages(config: str) -> str:
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
    return "amh+eng" if "eng" in installed else "amh"


def render_page(page: pymupdf.Page, dpi: int = OCR_DPI) -> Image.Image:
    """Render a PDF page to an RGB image without modifying the PDF."""
    pixmap = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
    with Image.open(BytesIO(pixmap.tobytes("png"))) as image:
        return image.convert("RGB")


def ocr_page(page: pymupdf.Page) -> str:
    """Recognize Amharic and English text on one rendered PDF page."""
    _configure_tesseract()
    tessdata_config = _tessdata_config()
    languages = _verify_languages(tessdata_config)
    image = render_page(page)
    try:
        return pytesseract.image_to_string(
            image,
            lang=languages,
            config=f"{tessdata_config} --oem 1 --psm 3".strip(),
        )
    except pytesseract.TesseractError as exc:
        raise OcrError(f"Tesseract OCR failed: {exc}") from exc
    finally:
        image.close()
