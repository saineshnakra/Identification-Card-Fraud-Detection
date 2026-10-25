# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-25

### Added

- Installable package with an `id-tamper-check` console script (also `python -m id_tamper_check`).
- `--align`: ORB feature matching + RANSAC homography, refined to sub-pixel accuracy with ECC, for phone photos taken
  at an angle.
- `--demo`: zero-input run on a synthetic specimen card photographed at an angle.
- `--json` machine-readable output and `--fail-under SCORE` exit threshold for scripts and CI.
- `--min-difference` sensitivity floor.
- `heatmap.png` and a one-page `report.png` summary sheet.
- In-memory API: `compare_images()` on NumPy arrays, `Region` boxes, `ComparisonResult.to_dict()` and
  `changed_area_ratio`.
- Synthetic specimen generator (`id_tamper_check.samples`), example images, and a benchmark script.
- Gradio web demo ready for Hugging Face Spaces, and an Open-in-Colab notebook.
- EXIF orientation is honored when loading photos.

### Changed

- SSIM uses the Gaussian-weighted formulation of Wang et al. (2004) on lightly blurred grayscale images.
- Pixels must exceed an absolute dissimilarity floor as well as Otsu's threshold, so genuine captures no longer
  produce noise "regions".
- Nearby fragments, such as the characters of an edited field, are merged into one region; regions are sorted by
  area. The default `min_region_area_ratio` is now `0.0005`.
- Annotated images in `ComparisonResult` are RGB (converted to BGR only when saved).
- CLI errors print a one-line message and exit with status 2 instead of a traceback.

## [0.1.0] - 2026-07-18

- Turned the original Colab notebook into a tested local command-line tool with CI.

## 2023-07-08

- Original Colab notebook and [Medium article](https://saineshnakra.medium.com/fake-id-card-detection-system-using-computer-vision-af3feea226fe).

[Unreleased]: https://github.com/saineshnakra/Identification-Card-Fraud-Detection/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/saineshnakra/Identification-Card-Fraud-Detection/releases/tag/v0.2.0
[0.1.0]: https://github.com/saineshnakra/Identification-Card-Fraud-Detection/commit/27b41c3
