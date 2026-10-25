"""Measure detection and false-positive rates on randomized synthetic captures.

Each trial renders a specimen card, optionally edits one or two fields,
"photographs" it at a random angle with noise and uneven lighting, and runs
the aligned comparison against the clean reference.

Run from the repository root:  python scripts/benchmark.py --trials 100
"""

from __future__ import annotations

import argparse
import random
import statistics
import time
from dataclasses import replace

from id_tamper_check import compare_images
from id_tamper_check.samples import SpecimenFields, render_specimen, simulate_capture

# Approximate layout boxes (left, top, right, bottom) of each editable field.
FIELD_BOXES = {
    "hair": (40, 120, 260, 400),
    "name": (300, 140, 600, 175),
    "date_of_birth": (300, 196, 600, 231),
    "document_number": (300, 308, 600, 343),
    "expiry": (300, 364, 600, 399),
}
EDITS = {
    "hair": ["long"],
    "name": ["JANE Q. SAMPLES", "JANE O. SAMPLE", "JUNE Q. SAMPLE"],
    "date_of_birth": ["14 MAR 1981", "14 MAR 1997", "11 MAR 1991", "14 MAY 1991"],
    "document_number": ["X 0482 1931", "X 0432 1937", "X 0482 7731"],
    "expiry": ["31 DEC 2036", "31 DEC 2081", "21 DEC 2031"],
}


def overlaps(region, box) -> bool:
    left, top, right, bottom = box
    return (
        region.x < right
        and region.x + region.width > left
        and region.y < bottom
        and region.y + region.height > top
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--trials", type=int, default=50, help="Trials per class (default: 50)")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    reference = render_specimen()
    genuine_scores, tampered_scores = [], []
    false_positives = detected = fields_total = fields_found = 0
    started = time.perf_counter()

    for trial in range(args.trials):
        angle = rng.uniform(-20, 20)
        photo = simulate_capture(reference, angle=angle, seed=trial)
        result = compare_images(reference, photo, align=True)
        genuine_scores.append(result.score)
        false_positives += bool(result.regions)

        edited = rng.sample(sorted(EDITS), k=rng.choice([1, 2]))
        fields = replace(SpecimenFields(), **{name: rng.choice(EDITS[name]) for name in edited})
        photo = simulate_capture(render_specimen(fields), angle=angle, seed=10_000 + trial)
        result = compare_images(reference, photo, align=True)
        tampered_scores.append(result.score)
        detected += bool(result.regions)
        fields_total += len(edited)
        fields_found += sum(any(overlaps(r, FIELD_BOXES[name]) for r in result.regions) for name in edited)

    elapsed = time.perf_counter() - started
    n = args.trials
    print(f"Trials: {n} genuine + {n} tampered captures, rotation within ±20°")
    print(f"Tampered cards flagged:      {detected / n:.0%}")
    print(f"Edited fields localized:     {fields_found / fields_total:.0%} ({fields_found}/{fields_total})")
    print(f"Genuine cards flagged (FP):  {false_positives / n:.0%}")
    print(f"SSIM genuine:  {statistics.mean(genuine_scores):.4f} ± {statistics.stdev(genuine_scores):.4f}")
    print(f"SSIM tampered: {statistics.mean(tampered_scores):.4f} ± {statistics.stdev(tampered_scores):.4f}")
    print(f"Mean time per comparison: {elapsed / (2 * n):.2f} s")


if __name__ == "__main__":
    main()
