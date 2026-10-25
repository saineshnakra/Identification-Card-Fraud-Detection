"""Command-line interface for ``id-tamper-check``."""

from __future__ import annotations

import argparse
from pathlib import Path

from .core import compare_documents, save_result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="id-tamper-check",
        description="Visualize structural differences between two aligned document images.",
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    result = compare_documents(
        args.reference,
        args.candidate,
        min_region_area_ratio=args.min_region_area_ratio,
    )
    save_result(result, args.output_dir)
    print(f"SSIM score: {result.score:.4f}")
    print(f"Changed regions: {len(result.regions)}")
    print(f"Results saved to: {args.output_dir}")
