"""
feature_matching.py
--------------------
Module 2 of the pipeline: FEATURE MATCHING.

Goal: given keypoints+descriptors from image A and image B, find pairs
of keypoints that describe the SAME physical point in the scene.

Method: for every descriptor in A, find its two nearest-neighbor
descriptors in B (by Euclidean distance in the 128-dim SIFT space).
Then apply Lowe's ratio test: a match is only kept if the best match
is meaningfully closer than the second-best match. Intuition — if a
descriptor is nearly equidistant from two different points in B, it's
ambiguous and likely to be a wrong match, so we throw it away.

This still leaves some wrong matches (outliers), which is exactly
why the next module (homography.py) uses RANSAC.
"""

import cv2
import numpy as np
from src.utils import log


def match_features(descriptors_a: np.ndarray, descriptors_b: np.ndarray,
                    ratio_thresh: float = 0.75):
    """Match descriptors from image A to image B using Lowe's ratio test.

    Parameters
    ----------
    descriptors_a, descriptors_b : np.ndarray
        SIFT descriptor arrays from detect_features().
    ratio_thresh : float
        Lowe's ratio threshold (0.7-0.8 is standard; lower = stricter).

    Returns
    -------
    good_matches : list[cv2.DMatch]
        Matches that passed the ratio test.
    """
    # BFMatcher = brute-force matcher: compares every descriptor in A
    # against every descriptor in B. NORM_L2 is the correct distance
    # metric for SIFT's floating-point descriptors.
    matcher = cv2.BFMatcher(cv2.NORM_L2)

    # k=2: for each descriptor in A, return its 2 nearest neighbors in B.
    knn_matches = matcher.knnMatch(descriptors_a, descriptors_b, k=2)

    good_matches = []
    for pair in knn_matches:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)

    log(f"Found {len(good_matches)} good matches after ratio test "
        f"(out of {len(knn_matches)} candidate pairs)")

    if len(good_matches) < 4:
        raise RuntimeError(
            "Fewer than 4 good matches found — cannot compute a homography. "
            "The two images may not overlap enough."
        )

    return good_matches


def get_matched_points(keypoints_a, keypoints_b, matches):
    """Convert cv2.DMatch objects into two aligned arrays of (x, y) coordinates.

    points_a[i] and points_b[i] refer to the SAME physical scene point,
    just as seen in image A and image B respectively. This is exactly
    the format homography estimation needs.
    """
    points_a = np.float32([keypoints_a[m.queryIdx].pt for m in matches])
    points_b = np.float32([keypoints_b[m.trainIdx].pt for m in matches])
    return points_a, points_b


def draw_matches(image_a, keypoints_a, image_b, keypoints_b, matches, max_draw=50):
    """Return a side-by-side visualization of the matches (for report screenshots)."""
    return cv2.drawMatches(
        image_a, keypoints_a, image_b, keypoints_b,
        matches[:max_draw], None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
