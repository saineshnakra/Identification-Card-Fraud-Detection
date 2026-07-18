"""Visualize structural differences between two aligned document images."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity


@dataclass(frozen=True)
class ComparisonResult:
    """Computed SSIM artifacts and the regions selected for annotation."""

    score: float
    regions: tuple[tuple[int, int, int, int], ...]
    reference_annotated: np.ndarray
    candidate_annotated: np.ndarray
    difference: np.ndarray
    threshold: np.ndarray


def _load_rgb(path: Path) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    try:
        with Image.open(path) as image:
            return np.asarray(image.convert("RGB"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Could not decode image: {path}") from error


def compare_documents(
    reference_path: Path,
    candidate_path: Path,
    min_region_area_ratio: float = 0.001,
) -> ComparisonResult:
    """Compare images and return explainable difference artifacts.

    The candidate is resized to match the reference. This normalizes dimensions
    but does not solve rotation, perspective, or capture-condition differences.
    """
    if not 0 <= min_region_area_ratio < 1:
        raise ValueError("min_region_area_ratio must be between 0 (inclusive) and 1 (exclusive).")

    reference_rgb = _load_rgb(reference_path)
    candidate_rgb = _load_rgb(candidate_path)
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
        cv2.boundingRect(contour)
        for contour in contours
        if cv2.contourArea(contour) >= minimum_area
    )

    reference_annotated = cv2.cvtColor(reference_rgb, cv2.COLOR_RGB2BGR)
    candidate_annotated = cv2.cvtColor(candidate_rgb, cv2.COLOR_RGB2BGR)
    for x, y, region_width, region_height in regions:
        top_left = (x, y)
        bottom_right = (x + region_width, y + region_height)
        cv2.rectangle(reference_annotated, top_left, bottom_right, (0, 0, 255), 2)
        cv2.rectangle(candidate_annotated, top_left, bottom_right, (0, 0, 255), 2)

    return ComparisonResult(
        score=float(score),
        regions=regions,
        reference_annotated=reference_annotated,
        candidate_annotated=candidate_annotated,
        difference=difference,
        threshold=threshold,
    )


def save_result(result: ComparisonResult, output_dir: Path) -> None:
    """Save comparison artifacts, raising if an image cannot be written."""
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "reference_annotated.png": result.reference_annotated,
        "candidate_annotated.png": result.candidate_annotated,
        "difference.png": result.difference,
        "threshold.png": result.threshold,
    }

    for filename, image in artifacts.items():
        destination = output_dir / filename
        if not cv2.imwrite(str(destination), image):
            raise OSError(f"Could not write image: {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize structural differences between two aligned document images."
    )
    parser.add_argument("reference", type=Path, help="Path to the trusted reference image")
    parser.add_argument("candidate", type=Path, help="Path to the candidate image")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("comparison"),
        help="Directory for annotated outputs (default: comparison)",
    )
    parser.add_argument(
        "--min-region-area-ratio",
        type=float,
        default=0.001,
        help="Ignore contours smaller than this fraction of the image area (default: 0.001)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = compare_documents(
        args.reference,
        args.candidate,
        min_region_area_ratio=args.min_region_area_ratio,
    )
    save_result(result, args.output_dir)
    print(f"SSIM score: {result.score:.4f}")
    print(f"Changed regions: {len(result.regions)}")
    print(f"Results saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
