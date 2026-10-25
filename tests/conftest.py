from pathlib import Path

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def write_image(tmp_path: Path):
    """Save an RGB array to ``tmp_path`` and return its path."""

    def _write(name: str, pixels: np.ndarray) -> Path:
        path = tmp_path / name
        Image.fromarray(pixels.astype(np.uint8)).save(path)
        return path

    return _write


@pytest.fixture
def blank() -> np.ndarray:
    return np.full((120, 180, 3), 240, dtype=np.uint8)


@pytest.fixture
def edited(blank: np.ndarray) -> np.ndarray:
    candidate = blank.copy()
    candidate[35:85, 60:125] = 25
    return candidate
