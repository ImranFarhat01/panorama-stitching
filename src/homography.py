"""
homography.py
--------------
Module 3a of the pipeline: HOMOGRAPHY ESTIMATION (Direct Linear Transform).

A homography H is a 3x3 matrix that maps a point (x, y) in image B to
a point (x', y') in image A, in homogeneous coordinates:

    [x']   [h1 h2 h3] [x]
    [y'] ~ [h4 h5 h6] [y]      (~ means "equal up to scale")
    [w']   [h7 h8 h9] [1]

    x' = (h1*x + h2*y + h3) / (h7*x + h8*y + h9)
    y' = (h4*x + h5*y + h6) / (h7*x + h8*y + h9)

DLT (Direct Linear Transform) finds H from >= 4 point correspondences
by rearranging the equations above into a linear system A h = 0 and
solving for h via SVD, exactly as covered in the course notes on
homography estimation.
"""

import numpy as np


def normalize_points(points: np.ndarray):
    """Hartley normalization: shift points so their centroid is the origin
    and scale them so the average distance from the origin is sqrt(2).

    Why: DLT is solved by SVD on a matrix built directly from raw pixel
    coordinates (which can be in the thousands). Without normalization,
    the linear system is numerically ill-conditioned and the solution
    becomes inaccurate. This is a standard, well-known fix (Hartley,
    1997) and is worth explicitly calling out in the report as a design
    decision, since it is easy to skip and quietly get a worse result.

    Returns
    -------
    normalized_points : np.ndarray, shape (N, 2)
    T : np.ndarray, shape (3, 3)
        The similarity transform used, so it can be undone later.
    """
    centroid = points.mean(axis=0)
    shifted = points - centroid
    mean_dist = np.mean(np.sqrt(np.sum(shifted ** 2, axis=1)))
    if mean_dist < 1e-8:
        mean_dist = 1e-8
    scale = np.sqrt(2) / mean_dist

    T = np.array([
        [scale, 0,     -scale * centroid[0]],
        [0,     scale, -scale * centroid[1]],
        [0,     0,     1],
    ])

    ones = np.ones((points.shape[0], 1))
    homogeneous = np.hstack([points, ones])
    normalized = (T @ homogeneous.T).T
    return normalized[:, :2], T


def compute_homography_dlt(points_a: np.ndarray, points_b: np.ndarray) -> np.ndarray:
    """Estimate the homography mapping points_b -> points_a using normalized DLT.

    Parameters
    ----------
    points_a, points_b : np.ndarray, shape (N, 2), N >= 4
        Matched point coordinates; points_b[i] maps to points_a[i].

    Returns
    -------
    H : np.ndarray, shape (3, 3)
        The estimated homography, normalized so H[2, 2] == 1.
    """
    if points_a.shape[0] < 4 or points_b.shape[0] < 4:
        raise ValueError("Need at least 4 point correspondences to compute a homography")

    # Step 1: normalize both point sets for numerical stability.
    norm_a, T_a = normalize_points(points_a)
    norm_b, T_b = normalize_points(points_b)

    # Step 2: build the 2N x 9 linear system A h = 0.
    n = norm_a.shape[0]
    A = np.zeros((2 * n, 9))
    for i in range(n):
        x, y = norm_b[i]
        xp, yp = norm_a[i]
        A[2 * i] = [-x, -y, -1, 0, 0, 0, x * xp, y * xp, xp]
        A[2 * i + 1] = [0, 0, 0, -x, -y, -1, x * yp, y * yp, yp]

    # Step 3: solve via SVD. The solution h is the singular vector
    # corresponding to the smallest singular value of A (last row of V^T).
    _, _, Vt = np.linalg.svd(A)
    h = Vt[-1]
    H_norm = h.reshape(3, 3)

    # Step 4: undo the normalization: H = T_a^-1 * H_norm * T_b
    H = np.linalg.inv(T_a) @ H_norm @ T_b

    # Normalize so the bottom-right element is 1 (standard convention).
    if abs(H[2, 2]) > 1e-8:
        H = H / H[2, 2]

    return H


def apply_homography(H: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Project points through homography H (handles the perspective divide)."""
    ones = np.ones((points.shape[0], 1))
    homogeneous = np.hstack([points, ones])
    projected = (H @ homogeneous.T).T
    # Perspective divide: divide by the homogeneous w-coordinate.
    w = projected[:, 2:3]
    w[w == 0] = 1e-8
    return projected[:, :2] / w


def reprojection_error(H: np.ndarray, points_a: np.ndarray, points_b: np.ndarray) -> np.ndarray:
    """Per-point Euclidean distance between the true point_a and H applied to point_b.

    This is the metric RANSAC uses to decide whether a match is an
    inlier (consistent with H) or an outlier.
    """
    projected = apply_homography(H, points_b)
    return np.sqrt(np.sum((projected - points_a) ** 2, axis=1))
