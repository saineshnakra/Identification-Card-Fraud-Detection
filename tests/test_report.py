import numpy as np

from id_tamper_check import compare_images, heatmap_overlay, render_report


def test_heatmap_matches_candidate_shape(blank, edited):
    result = compare_images(blank, edited)
    overlay = heatmap_overlay(result)

    assert overlay.shape == result.candidate_annotated.shape
    assert overlay.dtype == np.uint8


def test_report_is_a_two_by_two_sheet_with_header(blank, edited):
    report = render_report(compare_images(blank, edited))

    assert report.ndim == 3 and report.shape[2] == 3
    assert report.shape[1] == 2 * blank.shape[1]
    assert report.shape[0] > 2 * blank.shape[0]


def test_large_panels_are_downscaled():
    large = np.full((600, 1000, 3), 200, dtype=np.uint8)
    report = render_report(compare_images(large, large))

    assert report.shape[1] == 1600
