"""
Unit tests for src/homography.py.

Strategy: construct a KNOWN homography, use it to generate synthetic
point correspondences, then check that compute_homography_dlt()
recovers a homography that reproduces those correspondences accurately.
This validates the math independent of any real image or SIFT features.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.homography import compute_homography_dlt, apply_homography, reprojection_error


def make_known_homography():
    """A homography combining rotation, translation, and mild perspective."""
    theta = np.radians(8)
    H = np.array([
        [np.cos(theta), -np.sin(theta), 40],
        [np.sin(theta),  np.cos(theta), 15],
        [0.0002,          0.0001,        1],
    ])
    return H


def test_dlt_recovers_known_homography_exactly():
    """With noise-free correspondences, DLT should reproduce the mapping almost exactly."""
    H_true = make_known_homography()

    rng = np.random.default_rng(0)
    points_b = rng.uniform(0, 500, size=(20, 2)).astype(np.float64)
    points_a = apply_homography(H_true, points_b)

    H_est = compute_homography_dlt(points_a, points_b)

    errors = reprojection_error(H_est, points_a, points_b)
    assert np.all(errors < 1e-6), f"Max reprojection error too high: {errors.max()}"


def test_dlt_raises_on_too_few_points():
    points = np.array([[0, 0], [1, 1], [2, 2]], dtype=np.float64)
    with pytest.raises(ValueError):
        compute_homography_dlt(points, points)


def test_apply_homography_identity():
    """Applying the identity homography should return the same points."""
    H_identity = np.eye(3)
    points = np.array([[10, 20], [30, 40]], dtype=np.float64)
    projected = apply_homography(H_identity, points)
    assert np.allclose(projected, points)
