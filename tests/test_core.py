import json

import numpy as np
import pytest
from PIL import Image

from id_tamper_check import Region, compare_documents, compare_images, load_image, save_result


def test_identical_images_score_one_and_have_no_regions(blank):
    result = compare_images(blank, blank)

    assert result.score == pytest.approx(1.0, abs=1e-6)
    assert result.regions == ()
    assert not result.threshold.any()
    assert result.changed_area_ratio == 0


def test_changed_area_is_detected(blank, edited):
    result = compare_images(blank, edited)

    assert result.score < 1.0
    assert len(result.regions) >= 1
    largest = result.regions[0]
    assert isinstance(largest, Region)
    # The largest region should cover the edited block.
    assert largest.x <= 60 and largest.y <= 35
    assert largest.x + largest.width >= 125 and largest.y + largest.height >= 85


def test_regions_are_sorted_by_area(blank, edited):
    edited[5:15, 5:15] = 0
    result = compare_images(blank, edited, min_region_area_ratio=0)

    areas = [region.area for region in result.regions]
    assert areas == sorted(areas, reverse=True)


def test_candidate_is_resized_to_reference(blank):
    larger = np.full((240, 360, 3), 240, dtype=np.uint8)
    result = compare_images(blank, larger)

    assert result.candidate_annotated.shape == blank.shape
    assert result.score == pytest.approx(1.0, abs=1e-6)


def test_grayscale_and_rgba_inputs_are_accepted(blank):
    gray = np.full(blank.shape[:2], 240, dtype=np.uint8)
    rgba = np.dstack([blank, np.full(blank.shape[:2], 255, dtype=np.uint8)])

    assert compare_images(gray, rgba).score == pytest.approx(1.0, abs=1e-6)


def test_non_uint8_input_is_rejected(blank):
    with pytest.raises(ValueError, match="uint8"):
        compare_images(blank.astype(np.float32), blank)


@pytest.mark.parametrize("ratio", [-0.1, 1.0])
def test_invalid_area_ratio_is_rejected(tmp_path, ratio):
    with pytest.raises(ValueError, match="min_region_area_ratio"):
        compare_documents(tmp_path / "a.png", tmp_path / "b.png", min_region_area_ratio=ratio)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        compare_documents(tmp_path / "missing.png", tmp_path / "missing.png")


def test_undecodable_file_raises(tmp_path):
    bogus = tmp_path / "bogus.png"
    bogus.write_text("not an image")
    with pytest.raises(ValueError, match="decode"):
        compare_documents(bogus, bogus)


def test_to_dict_is_json_serializable(blank, edited):
    summary = compare_images(blank, edited).to_dict()

    assert json.loads(json.dumps(summary)) == summary
    assert summary["image_size"] == {"width": 180, "height": 120}
    assert summary["regions"][0]["mean_difference"] > 0


def test_documents_round_trip_and_outputs_are_saved(tmp_path, write_image, blank, edited):
    result = compare_documents(write_image("ref.png", blank), write_image("cand.png", edited))
    save_result(result, tmp_path / "out")

    for name in ("reference_annotated.png", "candidate_annotated.png", "difference.png", "threshold.png"):
        assert (tmp_path / "out" / name).is_file()


def test_exif_orientation_is_applied(tmp_path):
    path = tmp_path / "rotated.jpg"
    image = Image.new("RGB", (40, 20), (200, 200, 200))
    exif = image.getexif()
    exif[0x0112] = 6  # Orientation: rotate 90 degrees clockwise on display
    image.save(path, exif=exif)

    assert load_image(path).shape[:2] == (40, 20)
