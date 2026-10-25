"""Human-friendly visualizations of a :class:`~id_tamper_check.core.ComparisonResult`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from .core import ComparisonResult

PANEL_MAX_WIDTH = 800
HEADER_COLOR = (24, 28, 38)
TEXT_COLOR = (245, 245, 245)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def heatmap_overlay(result: ComparisonResult, opacity: float = 0.55) -> np.ndarray:
    """Blend a colored SSIM difference heatmap over the annotated candidate (RGB)."""
    heat = cv2.cvtColor(cv2.applyColorMap(result.difference, cv2.COLORMAP_INFERNO), cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(heat, opacity, result.candidate_annotated, 1 - opacity, 0)


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
    summary = (
        f"SSIM {result.score:.4f}   |   {region_count} changed region{'s' if region_count != 1 else ''}"
        f"   |   {result.changed_area_ratio:.1%} of area" + ("   |   auto-aligned" if result.aligned else "")
    )
    return np.vstack([_banner(summary, grid.shape[1], scale=0.8), grid])


def _fit(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    if width <= PANEL_MAX_WIDTH:
        return image
    scale = PANEL_MAX_WIDTH / width
    return cv2.resize(image, (PANEL_MAX_WIDTH, round(height * scale)), interpolation=cv2.INTER_AREA)


def _label(image: np.ndarray, title: str) -> np.ndarray:
    return np.vstack([_banner(title, image.shape[1], scale=0.6), image])


def _banner(text: str, width: int, scale: float) -> np.ndarray:
    scale *= max(width, 400) / 800
    thickness = max(1, round(scale * 2))
    (_, text_height), baseline = cv2.getTextSize(text, FONT, scale, thickness)
    height = text_height + baseline + round(20 * scale)
    banner = np.full((height, width, 3), HEADER_COLOR, dtype=np.uint8)
    origin = (round(14 * scale), (height + text_height) // 2)
    cv2.putText(banner, text, origin, FONT, scale, TEXT_COLOR, thickness, cv2.LINE_AA)
    return banner
