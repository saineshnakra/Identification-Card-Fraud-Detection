# Contributing

Thanks for helping improve **id-tamper-check**! Bug reports, docs fixes, new test cases and features are all welcome.

## Ground rules

- **Never commit real identity documents or personal data**, not even redacted ones. Use the synthetic generator in
  `id_tamper_check.samples` or images you own and are licensed to share.
- Keep the project honest: it visualizes image differences; it does not verify identity or score fraud. Please keep
  claims in docs and code consistent with that.
- Be kind. This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

```bash
git clone https://github.com/saineshnakra/Identification-Card-Fraud-Detection.git
cd Identification-Card-Fraud-Detection
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
pre-commit install
```

## Checks

```bash
ruff check .
ruff format --check .
pytest
python scripts/benchmark.py --trials 50   # if you touched the detection pipeline
```

If you change the detection pipeline, include before/after benchmark numbers in your pull request. If you change
anything visual, regenerate the README figures with `python scripts/generate_assets.py`.

## Pull requests

1. Open an issue first for larger changes so we can agree on the approach.
2. Keep each pull request focused, with tests for new behavior.
3. Add a line to the `Unreleased` section of [CHANGELOG.md](CHANGELOG.md).

## Good first issues

Look for the [`good first issue`](https://github.com/saineshnakra/Identification-Card-Fraud-Detection/labels/good%20first%20issue)
label, or pick something from the roadmap in the README.
