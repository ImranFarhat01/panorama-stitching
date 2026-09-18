"""
Unit tests for src/ransac.py.

Strategy: generate correspondences consistent with a known homography,
then CONTAMINATE a fraction of them with random outlier points. RANSAC
should still recover a homography close to the true one, and its
inlier mask should correctly flag the outliers as non-inliers.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.homography import apply_homography, reprojection_error
from src.ransac import ransac_homography


def make_known_homography():
    theta = np.radians(5)
    return np.array([
        [np.cos(theta), -np.sin(theta), 25],
        [np.sin(theta),  np.cos(theta), 10],
        [0.0001,          0.0,           1],
    ])


def test_ransac_recovers_homography_with_outliers():
    H_true = make_known_homography()
    rng = np.random.default_rng(1)

    n_inliers = 40
    n_outliers = 15

    points_b_inliers = rng.uniform(0, 500, size=(n_inliers, 2))
    points_a_inliers = apply_homography(H_true, points_b_inliers)

    # Outliers: random, unrelated point pairs (simulating bad matches).
    points_b_outliers = rng.uniform(0, 500, size=(n_outliers, 2))
    points_a_outliers = rng.uniform(0, 500, size=(n_outliers, 2))

    points_a = np.vstack([points_a_inliers, points_a_outliers])
    points_b = np.vstack([points_b_inliers, points_b_outliers])
    true_inlier_flags = np.array([True] * n_inliers + [False] * n_outliers)

    H_est, inlier_mask = ransac_homography(
        points_a, points_b, num_iterations=500, inlier_threshold=3.0
    )

    # RANSAC should mark most true inliers as inliers, and most true
    # outliers as outliers.
    correctly_classified = np.mean(inlier_mask == true_inlier_flags)
    assert correctly_classified > 0.9, f"Classification accuracy too low: {correctly_classified}"

    # The recovered homography should closely match ground truth on inlier points.
    errors = reprojection_error(H_est, points_a_inliers, points_b_inliers)
    assert errors.mean() < 2.0, f"Mean reprojection error too high: {errors.mean()}"
