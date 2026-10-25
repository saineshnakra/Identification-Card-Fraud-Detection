# ID Document Tampering Visualization with OpenCV and SSIM

[![CI](https://github.com/saineshnakra/Identification-Card-Fraud-Detection/actions/workflows/ci.yml/badge.svg)](https://github.com/saineshnakra/Identification-Card-Fraud-Detection/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?logo=python&logoColor=white)](https://www.python.org/)

An educational computer-vision baseline for comparing two aligned document images. It computes the Structural Similarity Index (SSIM), builds a pixel-level difference mask, finds changed regions with OpenCV contours, and saves annotated output images.

> **Important:** this is not an identity-verification or production fraud-detection system. An SSIM score is not a fraud probability. Real document authentication requires issuer validation, OCR and field checks, security-feature analysis, capture-quality controls, adversarial testing, and human review.

The project began as a Colab tutorial and is now packaged as a reproducible local command-line tool with tests and CI. The accompanying explanation is available in the [original Medium article](https://saineshnakra.medium.com/fake-id-card-detection-system-using-computer-vision-af3feea226fe).

## What it does

- Loads two local image files; no document is uploaded to a third-party API
- Normalizes the candidate image to the reference image dimensions
- Computes SSIM on grayscale images
- Converts structural differences into a binary mask
- Filters tiny contours and draws bounding boxes around changed regions
- Saves annotated reference, annotated candidate, difference, and threshold images

## Install

```bash
git clone https://github.com/saineshnakra/Identification-Card-Fraud-Detection.git
cd Identification-Card-Fraud-Detection
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

## Run

```bash
id-tamper-check reference.png candidate.png --output-dir comparison
```

Example output:

```text
SSIM score: 0.8732
Changed regions: 3
Results saved to: comparison
```

The command creates:

- `reference_annotated.png`
- `candidate_annotated.png`
- `difference.png`
- `threshold.png`

Use `--min-region-area-ratio` to control how aggressively tiny changed regions are ignored:

```bash
id-tamper-check reference.png candidate.png --min-region-area-ratio 0.002
```

## Use as a Python module

```python
from pathlib import Path

from id_tamper_check import compare_documents, save_result

result = compare_documents(Path("reference.png"), Path("candidate.png"))
print(result.score, result.regions)
save_result(result, Path("comparison"))
```

## How it works

1. Read both images and convert them to RGB.
2. Resize the candidate to the reference dimensions for pixel alignment.
3. Convert both images to grayscale.
4. Calculate SSIM and its per-pixel similarity map.
5. Convert the similarity map into a difference image.
6. Apply Otsu thresholding and find external contours.
7. Discard regions below the configured area ratio and annotate the remainder.

## Limitations

- The images must depict the same document layout and be closely aligned.
- Resizing does not correct rotation, perspective, glare, blur, compression, or lighting differences.
- A low score can come from capture conditions rather than tampering.
- A high score does not establish that a document is genuine.
- The method does not validate names, numbers, barcodes, faces, signatures, or issuer records.
- Do not commit real identity documents or other personal data to the repository.

Treat this as an explainable image-difference demo and a starting point for experimentation—not a KYC, compliance, or automated decision system.

## Test

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

## Author

Built by [Sainesh Nakra](https://sainesh.com/).
