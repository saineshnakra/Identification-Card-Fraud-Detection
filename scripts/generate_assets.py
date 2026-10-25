"""Regenerate the sample images in examples/ and the figures in docs/assets/.

Run from the repository root:  python scripts/generate_assets.py
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from id_tamper_check import align_to_reference, compare_images, heatmap_overlay, render_report
from id_tamper_check.samples import render_specimen, simulate_capture, specimen_pair

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
ASSETS = ROOT / "docs" / "assets"


def save(image, path: Path, **options) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(path, optimize=True, **options)
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


def main() -> None:
    reference, tampered = specimen_pair()
    photo = simulate_capture(tampered)
    save(reference, EXAMPLES / "specimen_reference.png")
    save(tampered, EXAMPLES / "specimen_tampered.png")
    save(photo, EXAMPLES / "specimen_tampered_photo.jpg", quality=90)
    save(
        simulate_capture(render_specimen(), angle=5.0, seed=1),
        EXAMPLES / "specimen_genuine_photo.jpg",
        quality=90,
    )

    result = compare_images(reference, photo, align=True)
    save(render_report(result), ASSETS / "demo-report.jpg", quality=88)
    save(pipeline_strip(reference, photo, result), ASSETS / "pipeline.jpg", quality=88)
    save(social_preview(photo, result), ASSETS / "social-preview.png")


def social_preview(photo, result) -> np.ndarray:
    """1280x640 card for the repository's social preview setting."""
    canvas = Image.new("RGB", (1280, 640), (17, 21, 31))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (64, 70), "ID Card Tampering Detection", font=ImageFont.load_default(size=56), fill=(255, 255, 255)
    )
    draw.text(
        (66, 148),
        "Find edited fields in document photos with OpenCV + SSIM",
        font=ImageFont.load_default(size=28),
        fill=(160, 190, 230),
    )
    for index, (image, title) in enumerate(
        ((photo, "Phone photo"), (result.candidate_annotated, "Flagged edits"))
    ):
        tile = Image.fromarray(image)
        tile.thumbnail((560, 360))
        left = 64 + index * 592
        canvas.paste(tile, (left, 236 + (360 - tile.height) // 2))
        draw.text((left, 606), title, font=ImageFont.load_default(size=22), fill=(200, 205, 215), anchor="lm")
    draw.text(
        (1216, 606),
        "id-tamper-check",
        font=ImageFont.load_default(size=22),
        fill=(120, 130, 150),
        anchor="rm",
    )
    return np.asarray(canvas)


def pipeline_strip(reference, photo, result) -> np.ndarray:
    """One labeled row showing each stage of the method."""
    stages = [
        ("1. Reference", reference),
        ("2. Phone photo", photo),
        ("3. Auto-aligned", align_to_reference(reference, photo).image),
        ("4. SSIM heatmap", heatmap_overlay(result)),
        ("5. Flagged edits", result.candidate_annotated),
    ]
    tiles = []
    box_width, box_height = 360, 250
    for title, image in stages:
        height, width = image.shape[:2]
        scale = min(box_width / width, box_height / height)
        tile = cv2.resize(image, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)
        canvas = np.full((box_height, box_width, 3), 255, dtype=np.uint8)
        top, left = (box_height - tile.shape[0]) // 2, (box_width - tile.shape[1]) // 2
        canvas[top : top + tile.shape[0], left : left + tile.shape[1]] = tile
        label = Image.new("RGB", (box_width, 44), (255, 255, 255))
        font = ImageFont.load_default(size=20)
        ImageDraw.Draw(label).text((box_width // 2, 22), title, font=font, fill=(30, 30, 30), anchor="mm")
        tiles.append(np.vstack([np.asarray(label), canvas]))
        tiles.append(np.full((tiles[-1].shape[0], 12, 3), 255, dtype=np.uint8))
    return np.hstack(tiles[:-1])


if __name__ == "__main__":
    main()
