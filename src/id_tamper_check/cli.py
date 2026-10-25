"""Command-line interface for ``id-tamper-check``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .align import AlignmentError
from .core import compare_documents, save_result

EXIT_OK = 0
EXIT_BELOW_THRESHOLD = 1
EXIT_ERROR = 2


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
    parser.add_argument(
        "--align",
        action="store_true",
        help="Register the candidate onto the reference first (for photos taken at an angle)",
    )
    parser.add_argument("--json", action="store_true", help="Print a machine-readable JSON summary")
    parser.add_argument(
        "--fail-under",
        type=float,
        metavar="SCORE",
        help="Exit with status 1 when the SSIM score is below SCORE (useful in scripts and CI)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = compare_documents(
            args.reference,
            args.candidate,
            min_region_area_ratio=args.min_region_area_ratio,
            align=args.align,
        )
        save_result(result, args.output_dir)
    except (AlignmentError, OSError, ValueError) as error:
        print(f"id-tamper-check: error: {error}", file=sys.stderr)
        return EXIT_ERROR

    if args.json:
        print(json.dumps({**result.to_dict(), "output_dir": str(args.output_dir)}, indent=2))
    else:
        print(f"SSIM score: {result.score:.4f}")
        print(f"Changed regions: {len(result.regions)}")
        print(f"Results saved to: {args.output_dir}")

    if args.fail_under is not None and result.score < args.fail_under:
        return EXIT_BELOW_THRESHOLD
    return EXIT_OK
