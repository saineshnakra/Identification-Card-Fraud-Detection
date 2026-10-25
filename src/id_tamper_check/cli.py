"""Command-line interface for ``id-tamper-check``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from . import __version__
from .align import AlignmentError
from .core import ComparisonResult, compare_documents, compare_images, save_result
from .samples import specimen_pair

EXIT_OK = 0
EXIT_BELOW_THRESHOLD = 1
EXIT_ERROR = 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="id-tamper-check",
        description="Highlight tampered regions between a reference ID/document image and a candidate.",
        epilog=(
            "examples:\n"
            "  id-tamper-check --demo\n"
            "  id-tamper-check reference.png scan.png\n"
            "  id-tamper-check reference.png phone_photo.jpg --align --json --fail-under 0.9"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("reference", type=Path, nargs="?", help="Path to the trusted reference image")
    parser.add_argument("candidate", type=Path, nargs="?", help="Path to the candidate image")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run on a built-in synthetic specimen card photographed at an angle (no inputs needed)",
    )
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
    args = parser.parse_args(argv)
    if args.demo and (args.reference or args.candidate):
        parser.error("--demo does not take reference or candidate paths")
    if not args.demo and not (args.reference and args.candidate):
        parser.error("reference and candidate paths are required (or use --demo)")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.demo:
            result = _run_demo(args.output_dir, args.min_region_area_ratio)
        else:
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
        print(f"Open {args.output_dir / 'report.png'} for the summary sheet.")

    if args.fail_under is not None and result.score < args.fail_under:
        return EXIT_BELOW_THRESHOLD
    return EXIT_OK


def _run_demo(output_dir: Path, min_region_area_ratio: float) -> ComparisonResult:
    reference, candidate = specimen_pair(capture=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, image in (("demo_reference.png", reference), ("demo_candidate.png", candidate)):
        Image.fromarray(image).save(output_dir / name)
    return compare_images(reference, candidate, min_region_area_ratio=min_region_area_ratio, align=True)
