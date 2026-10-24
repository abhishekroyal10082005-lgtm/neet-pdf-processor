from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import List

import cv2
import fitz
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from app.models import JobSettings


def safe_read_pdf_pages(file_path: str) -> List[str]:
    doc = fitz.open(file_path)
    pages: List[str] = []
    temp_dir = Path(file_path).parent / f"{uuid.uuid4()}_pages"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        matrix = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        out_path = temp_dir / f"page_{page_index + 1}.png"
        image.save(out_path)
        pages.append(str(out_path))

    doc.close()
    return pages


def normalize_image(image: Image.Image, settings: JobSettings) -> Image.Image:
    img = image.convert("RGB")
    if settings.background_normalization:
        img = ImageOps.autocontrast(img)
        img = ImageEnhance.Contrast(img).enhance(1.2)
    if settings.denoise:
        img = img.filter(ImageFilter.MedianFilter(size=3))
    if settings.sharpen:
        img = img.filter(ImageFilter.SHARPEN)
    if settings.contrast:
        img = ImageEnhance.Contrast(img).enhance(1.3)
    if settings.deblur:
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=140, threshold=3))
    return img


def make_processed_pdf(page_paths: List[str], output_path: str, dpi: int = 300) -> None:
    if not page_paths:
        raise ValueError("No processed pages available for export.")

    doc = fitz.open()
    for image_path in page_paths:
        img = Image.open(image_path)
        rgb_img = img.convert("RGB")
        converted_path = str(Path(image_path).with_suffix(".converted.png"))
        rgb_img.save(converted_path, dpi=(dpi, dpi))
        page = doc.new_page(width=rgb_img.width, height=rgb_img.height)
        page.insert_image(page.rect, filename=converted_path)
    doc.save(output_path)
    doc.close()


def validate_output_file(output_path: str) -> bool:
    return os.path.exists(output_path) and os.path.getsize(output_path) > 1024


def process_pdf_file(file_path: str, output_path: str, settings: JobSettings, progress_callback=None) -> None:
    page_paths = safe_read_pdf_pages(file_path)
    if not page_paths:
        raise ValueError("Document contains no pages to process.")

    processed_paths: List[str] = []
    for index, page_path in enumerate(page_paths, start=1):
        img = Image.open(page_path).convert("RGB")
        normalized = normalize_image(img, settings)
        cleaned_path = str(Path(page_path).with_name(f"processed_{index}.png"))
        normalized.save(cleaned_path)
        processed_paths.append(cleaned_path)
        if progress_callback:
            percentage = int((index / len(page_paths)) * 100)
            progress_callback(index, len(page_paths), percentage)

    make_processed_pdf(processed_paths, output_path, dpi=settings.output_dpi)
    if not validate_output_file(output_path):
        raise RuntimeError("Processed output PDF failed validation.")

    for page_path in page_paths + processed_paths:
        try:
            os.remove(page_path)
        except FileNotFoundError:
            pass

    # Clean temporary converted PNGs created by make_processed_pdf.
    for item in Path(output_path).parent.iterdir():
        if item.suffix.lower() in {".png"} and "converted" in item.name:
            try:
                item.unlink()
            except OSError:
                pass
