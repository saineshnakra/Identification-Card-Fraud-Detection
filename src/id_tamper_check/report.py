"""Human-friendly visualizations of a :class:`~id_tamper_check.core.ComparisonResult`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from .core import ComparisonResult

PANEL_MAX_WIDTH = 800
HEADER_COLOR = (24, 28, 38)
TEXT_COLOR = (245, 245, 245)


def heatmap_overlay(result: ComparisonResult, opacity: float = 0.75) -> np.ndarray:
    """Overlay a colored SSIM difference heatmap on the annotated candidate (RGB).

    Each pixel's opacity scales with its difference, so unchanged areas keep
    their original appearance and edits glow.
    """
    heat = cv2.cvtColor(cv2.applyColorMap(result.difference, cv2.COLORMAP_TURBO), cv2.COLOR_BGR2RGB)
    alpha = (result.difference.astype(np.float32) / 255 * opacity)[..., None]
    blended = heat * alpha + result.candidate_annotated * (1 - alpha)
    return blended.round().astype(np.uint8)


def render_report(result: ComparisonResult) -> np.ndarray:
    """Render a 2x2 summary sheet with a header line of key numbers (RGB)."""
    panels = [
        ("Reference", result.reference_annotated),
        ("Candidate", result.candidate_annotated),
        ("SSIM difference heatmap", heatmap_overlay(result)),
        ("Changed-region mask", cv2.cvtColor(result.threshold, cv2.COLOR_GRAY2RGB)),
    ]
    labeled = [_label(_fit(image), title) for title, image in panels]
    grid = np.vstack([np.hstack(labeled[:2]), np.hstack(labeled[2:])])

    region_count = len(result.regions)
    parts = [
        f"SSIM {result.score:.4f}",
        f"{region_count} changed region{'s' if region_count != 1 else ''}",
        f"{result.changed_area_ratio:.1%} of area flagged",
    ]
    if result.aligned:
        parts.append("auto-aligned")
    return np.vstack([_banner("   ·   ".join(parts), grid.shape[1], size=24), grid])


def _fit(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    if width <= PANEL_MAX_WIDTH:
        return image
    scale = PANEL_MAX_WIDTH / width
    return cv2.resize(image, (PANEL_MAX_WIDTH, round(height * scale)), interpolation=cv2.INTER_AREA)


def _label(image: np.ndarray, title: str) -> np.ndarray:
    return np.vstack([_banner(title, image.shape[1], size=18), image])


def _banner(text: str, width: int, size: int) -> np.ndarray:
    size = max(10, round(size * max(width, 400) / 800))
    font = ImageFont.load_default(size=size)
    while size > 10 and font.getlength(text) > width - size * 1.4:
        size -= 1
        font = ImageFont.load_default(size=size)
    height = round(size * 1.9)
    banner = Image.new("RGB", (width, height), HEADER_COLOR)
    ImageDraw.Draw(banner).text(
        (round(size * 0.7), height // 2), text, font=font, fill=TEXT_COLOR, anchor="lm"
    )
    return np.asarray(banner)
