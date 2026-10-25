import cv2
import numpy as np
import pytest

from id_tamper_check import AlignmentError, align_to_reference, compare_images


@pytest.fixture
def textured() -> np.ndarray:
    """A deterministic image with enough corners for ORB to latch onto."""
    rng = np.random.default_rng(7)
    image = np.full((400, 640, 3), 235, dtype=np.uint8)
    for _ in range(120):
        x, y = rng.integers(0, 600), rng.integers(0, 370)
        w, h = rng.integers(8, 40), rng.integers(8, 30)
        color = tuple(int(c) for c in rng.integers(0, 200, 3))
        cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)), color, -1)
    return image


def _photograph(image: np.ndarray) -> np.ndarray:
    """Simulate a handheld capture: rotate, scale and pad onto a larger canvas."""
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 6, 0.8)
    matrix[:, 2] += (60, 40)
    return cv2.warpAffine(image, matrix, (width + 120, height + 80), borderValue=(90, 90, 90))


def test_alignment_recovers_a_rotated_capture(textured):
    capture = _photograph(textured)

    unaligned = compare_images(textured, capture)
    aligned = compare_images(textured, capture, align=True)

    assert aligned.aligned is True
    assert aligned.score > 0.9
    assert aligned.score > unaligned.score + 0.3


def test_alignment_localizes_an_edit(textured):
    edited = textured.copy()
    cv2.rectangle(edited, (300, 150), (380, 210), (20, 20, 160), -1)
    result = compare_images(textured, _photograph(edited), align=True)

    largest = result.regions[0]
    assert abs(largest.x - 300) < 15 and abs(largest.y - 150) < 15


def test_alignment_returns_valid_mask(textured):
    alignment = align_to_reference(textured, _photograph(textured))

    assert alignment.image.shape == textured.shape
    assert alignment.valid_mask.shape == textured.shape[:2]
    assert alignment.inliers >= 15


def test_featureless_images_raise_alignment_error():
    flat = np.full((200, 300, 3), 128, dtype=np.uint8)
    with pytest.raises(AlignmentError):
        compare_images(flat, flat, align=True)
