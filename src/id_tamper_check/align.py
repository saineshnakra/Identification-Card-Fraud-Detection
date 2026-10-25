"""Feature-based alignment of a candidate photo onto a reference image."""

from __future__ import annotations

from typing import NamedTuple

import cv2
import numpy as np


class AlignmentError(RuntimeError):
    """Raised when the candidate cannot be reliably registered to the reference."""


class Alignment(NamedTuple):
    """A candidate warped into reference coordinates and the mask of valid pixels."""

    image: np.ndarray
    valid_mask: np.ndarray
    homography: np.ndarray
    inliers: int


def align_to_reference(
    reference: np.ndarray,
    candidate: np.ndarray,
    max_features: int = 5000,
    ratio: float = 0.75,
    min_inliers: int = 15,
    refine: bool = True,
) -> Alignment:
    """Warp ``candidate`` onto ``reference`` using ORB features and a RANSAC homography.

    This corrects rotation, scale, translation and perspective from a handheld
    capture of a flat document. With ``refine=True`` the homography is then
    polished to sub-pixel accuracy with ECC image alignment, which removes
    the faint outlines a slightly-off feature match leaves in the SSIM map.
    It does not correct glare, blur or lighting. Both inputs must be RGB
    ``uint8`` arrays.
    """
    reference_gray = cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY)
    candidate_gray = cv2.cvtColor(candidate, cv2.COLOR_RGB2GRAY)

    orb = cv2.ORB_create(nfeatures=max_features)
    reference_keypoints, reference_descriptors = orb.detectAndCompute(reference_gray, None)
    candidate_keypoints, candidate_descriptors = orb.detectAndCompute(candidate_gray, None)
    if reference_descriptors is None or candidate_descriptors is None:
        raise AlignmentError("Not enough texture to detect features in one of the images.")

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    pairs = matcher.knnMatch(candidate_descriptors, reference_descriptors, k=2)
    good = [pair[0] for pair in pairs if len(pair) == 2 and pair[0].distance < ratio * pair[1].distance]
    if len(good) < min_inliers:
        raise AlignmentError(f"Only {len(good)} feature matches found; need at least {min_inliers}.")

    source = np.float32([candidate_keypoints[match.queryIdx].pt for match in good]).reshape(-1, 1, 2)
    destination = np.float32([reference_keypoints[match.trainIdx].pt for match in good]).reshape(-1, 1, 2)
    homography, inlier_mask = cv2.findHomography(source, destination, cv2.RANSAC, 5.0)
    inliers = int(inlier_mask.sum()) if inlier_mask is not None else 0
    if homography is None or inliers < min_inliers:
        raise AlignmentError(f"Only {inliers} consistent feature matches; need at least {min_inliers}.")

    height, width = reference.shape[:2]
    if refine:
        homography = _refine_with_ecc(reference_gray, candidate_gray, homography)
    warped = cv2.warpPerspective(candidate, homography, (width, height), flags=cv2.INTER_LINEAR)
    coverage = cv2.warpPerspective(
        np.full(candidate.shape[:2], 255, dtype=np.uint8),
        homography,
        (width, height),
        flags=cv2.INTER_NEAREST,
    )
    # Pull the mask in slightly so SSIM windows straddling the warp border, and
    # the resampled document edge itself, are ignored.
    valid_mask = cv2.erode(coverage, np.ones((7, 7), np.uint8)) > 0
    margin = max(4, round(0.01 * min(height, width)))
    valid_mask[:margin, :] = valid_mask[-margin:, :] = False
    valid_mask[:, :margin] = valid_mask[:, -margin:] = False
    return Alignment(warped, valid_mask, homography, inliers)


def _refine_with_ecc(
    reference_gray: np.ndarray,
    candidate_gray: np.ndarray,
    homography: np.ndarray,
    max_side: int = 1000,
) -> np.ndarray:
    """Polish ``homography`` with ECC maximization, falling back to it on failure."""
    height, width = reference_gray.shape
    scale = min(1.0, max_side / max(height, width))
    to_small = np.diag([scale, scale, 1.0])
    size = (round(width * scale), round(height * scale))

    template = cv2.resize(reference_gray, size, interpolation=cv2.INTER_AREA).astype(np.float32)
    coarse = cv2.warpPerspective(candidate_gray, to_small @ homography, size, flags=cv2.INTER_LINEAR)
    correction = np.eye(3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-6)
    try:
        _, correction = cv2.findTransformECC(
            template, coarse.astype(np.float32), correction, cv2.MOTION_HOMOGRAPHY, criteria, None, 5
        )
    except cv2.error:
        return homography

    # ECC maps template coordinates into the coarse warp; invert it and lift
    # it back to full resolution before composing with the feature homography.
    full_correction = np.linalg.inv(to_small) @ np.linalg.inv(correction.astype(np.float64)) @ to_small
    return full_correction @ homography
