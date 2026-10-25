from id_tamper_check import compare_images
from id_tamper_check.samples import CARD_SIZE, render_specimen, specimen_pair


def test_specimen_is_deterministic_and_card_sized():
    first, second = render_specimen(), render_specimen()

    assert first.shape == (CARD_SIZE[1], CARD_SIZE[0], 3)
    assert (first == second).all()


def _overlaps(region, box):
    x, y, right, bottom = box
    return (
        region.x < right
        and region.x + region.width > x
        and region.y < bottom
        and region.y + region.height > y
    )


def test_tampered_fields_are_all_flagged():
    reference, tampered = specimen_pair()
    regions = compare_images(reference, tampered).regions

    portrait = (40, 120, 260, 400)
    date_of_birth = (300, 190, 560, 230)
    document_number = (300, 300, 560, 345)
    for box in (portrait, date_of_birth, document_number):
        assert any(_overlaps(region, box) for region in regions), box


def test_simulated_capture_needs_alignment():
    reference, capture = specimen_pair(capture=True)

    assert capture.shape != reference.shape
    aligned = compare_images(reference, capture, align=True)
    assert aligned.score > compare_images(reference, capture).score
    assert len(aligned.regions) >= 3
