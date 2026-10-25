"""Core SSIM comparison for two document images."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity

ANNOTATION_COLOR = (255, 0, 0)


class Region(NamedTuple):
    """Bounding box of a changed region, in reference-image pixel coordinates."""

    x: int
    y: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass(frozen=True)
class ComparisonResult:
    """Computed SSIM artifacts and the regions selected for annotation.

    Annotated images are RGB arrays; ``difference`` and ``threshold`` are
    single-channel ``uint8`` arrays where brighter means more different.
    """

    score: float
    regions: tuple[Region, ...]
    reference_annotated: np.ndarray
    candidate_annotated: np.ndarray
    difference: np.ndarray
    threshold: np.ndarray

    @property
    def changed_area_ratio(self) -> float:
        """Fraction of the image covered by the thresholded difference mask."""
        return float(np.count_nonzero(self.threshold)) / self.threshold.size

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary of the comparison."""
        height, width = self.difference.shape[:2]
        return {
            "score": round(self.score, 6),
            "changed_area_ratio": round(self.changed_area_ratio, 6),
            "image_size": {"width": width, "height": height},
            "regions": [
                {
                    **region._asdict(),
                    "area": region.area,
                    "mean_difference": round(float(self._region_pixels(region).mean()) / 255, 6),
                }
                for region in self.regions
            ],
        }

    def _region_pixels(self, region: Region) -> np.ndarray:
        return self.difference[region.y : region.y + region.height, region.x : region.x + region.width]


def load_image(path: Path) -> np.ndarray:
    """Load an image file as an RGB ``uint8`` array."""
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    try:
        with Image.open(path) as image:
            return np.asarray(image.convert("RGB"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Could not decode image: {path}") from error


def compare_images(
    reference: np.ndarray,
    candidate: np.ndarray,
    min_region_area_ratio: float = 0.001,
) -> ComparisonResult:
    """Compare two RGB arrays and return explainable difference artifacts.

    The candidate is resized to match the reference. This normalizes dimensions
    but does not solve rotation, perspective, or capture-condition differences.
    """
    _validate_area_ratio(min_region_area_ratio)
    reference_rgb = _as_rgb(reference)
    candidate_rgb = _as_rgb(candidate)
    height, width = reference_rgb.shape[:2]
    candidate_rgb = cv2.resize(candidate_rgb, (width, height), interpolation=cv2.INTER_AREA)

    reference_gray = cv2.cvtColor(reference_rgb, cv2.COLOR_RGB2GRAY)
    candidate_gray = cv2.cvtColor(candidate_rgb, cv2.COLOR_RGB2GRAY)
    score, similarity_map = structural_similarity(
        reference_gray,
        candidate_gray,
        full=True,
        data_range=255,
    )

    difference = np.clip((1.0 - similarity_map) * 255, 0, 255).astype(np.uint8)
    threshold = cv2.threshold(difference, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    minimum_area = height * width * min_region_area_ratio
    regions = tuple(
        sorted(
            (
                Region(*cv2.boundingRect(contour))
                for contour in contours
                if cv2.contourArea(contour) >= minimum_area
            ),
            key=lambda region: region.area,
            reverse=True,
        )
    )

    reference_annotated = reference_rgb.copy()
    candidate_annotated = candidate_rgb.copy()
    for region in regions:
        top_left = (region.x, region.y)
        bottom_right = (region.x + region.width, region.y + region.height)
        cv2.rectangle(reference_annotated, top_left, bottom_right, ANNOTATION_COLOR, 2)
        cv2.rectangle(candidate_annotated, top_left, bottom_right, ANNOTATION_COLOR, 2)

    return ComparisonResult(
        score=float(score),
        regions=regions,
        reference_annotated=reference_annotated,
        candidate_annotated=candidate_annotated,
        difference=difference,
        threshold=threshold,
    )


def compare_documents(
    reference_path: Path,
    candidate_path: Path,
    min_region_area_ratio: float = 0.001,
) -> ComparisonResult:
    """Load two image files and compare them with :func:`compare_images`."""
    _validate_area_ratio(min_region_area_ratio)
    return compare_images(
        load_image(Path(reference_path)),
        load_image(Path(candidate_path)),
        min_region_area_ratio=min_region_area_ratio,
    )


def save_result(result: ComparisonResult, output_dir: Path) -> None:
    """Save comparison artifacts, raising if an image cannot be written."""
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "reference_annotated.png": cv2.cvtColor(result.reference_annotated, cv2.COLOR_RGB2BGR),
        "candidate_annotated.png": cv2.cvtColor(result.candidate_annotated, cv2.COLOR_RGB2BGR),
        "difference.png": result.difference,
        "threshold.png": result.threshold,
    }

    for filename, image in artifacts.items():
        destination = output_dir / filename
        if not cv2.imwrite(str(destination), image):
            raise OSError(f"Could not write image: {destination}")


def _validate_area_ratio(min_region_area_ratio: float) -> None:
    if not 0 <= min_region_area_ratio < 1:
        raise ValueError("min_region_area_ratio must be between 0 (inclusive) and 1 (exclusive).")


def _as_rgb(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image)
    if image.dtype != np.uint8:
        raise ValueError("Images must be uint8 arrays.")
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    if image.ndim == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    if image.ndim == 3 and image.shape[2] == 3:
        return np.ascontiguousarray(image)
    raise ValueError(f"Unsupported image shape: {image.shape}")
