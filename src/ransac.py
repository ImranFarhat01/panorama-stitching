"""
ransac.py
---------
Module 3b of the pipeline: RANSAC (RANdom SAmple Consensus).

Problem: feature_matching.py still leaves some WRONG matches (outliers)
even after the ratio test. A single wrong match can badly corrupt a
least-squares DLT fit, since DLT tries to satisfy ALL points at once.

RANSAC's idea: repeatedly guess.
  1. Randomly pick the minimal number of correspondences needed (4, for
     a homography).
  2. Fit a homography to just those 4 points (cheap, exact).
  3. Check how many of the OTHER correspondences agree with this
     homography (within some pixel-distance threshold) -- these are
     the "inliers" for this guess.
  4. Repeat many times, keep the guess with the most inliers.
  5. Finally, refit the homography using ALL of that best guess's
     inliers (not just 4 points) for a more accurate final result.

Over enough iterations, a sample of 4 correct (inlier) matches is very
likely to be drawn at least once, and that sample will have far more
support (inliers) than any sample containing an outlier -- which is
what lets RANSAC find the correct model despite contamination.
"""

import numpy as np
from src.homography import compute_homography_dlt, reprojection_error
from src.utils import log


def ransac_homography(points_a: np.ndarray, points_b: np.ndarray,
                       num_iterations: int = 2000,
                       inlier_threshold: float = 4.0,
                       min_inliers: int = 10,
                       seed: int = 42):
    """Robustly estimate a homography from noisy point correspondences.

    Parameters
    ----------
    points_a, points_b : np.ndarray, shape (N, 2)
        Matched points; points_b[i] maps to points_a[i].
    num_iterations : int
        Number of random 4-point samples to try.
    inlier_threshold : float
        Max reprojection error (pixels) for a match to count as an inlier.
    min_inliers : int
        Minimum inliers required to accept the final model.
    seed : int
        RNG seed, for reproducible results (important for grading/demo
        reproducibility).

    Returns
    -------
    best_H : np.ndarray, shape (3, 3)
        Homography refit on all inliers of the best sample found.
    best_inlier_mask : np.ndarray, shape (N,), dtype=bool
        Which of the N input matches were inliers to best_H.
    """
    rng = np.random.default_rng(seed)
    n = points_a.shape[0]
    if n < 4:
        raise ValueError("Need at least 4 matches to run RANSAC")

    best_inlier_count = -1
    best_inlier_mask = None
    best_H = None

    for iteration in range(num_iterations):
        # Step 1: randomly sample 4 correspondences (the minimum needed).
        sample_idx = rng.choice(n, size=4, replace=False)
        sample_a = points_a[sample_idx]
        sample_b = points_b[sample_idx]

        # Step 2: fit a homography to just these 4 points.
        try:
            H_candidate = compute_homography_dlt(sample_a, sample_b)
        except np.linalg.LinAlgError:
            continue  # degenerate sample (e.g. collinear points); skip it

        # Step 3: count inliers among ALL matches, not just the sample.
        errors = reprojection_error(H_candidate, points_a, points_b)
        inlier_mask = errors < inlier_threshold
        inlier_count = int(np.sum(inlier_mask))

        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_inlier_mask = inlier_mask
            best_H = H_candidate

    if best_H is None or best_inlier_count < min_inliers:
        raise RuntimeError(
            f"RANSAC failed to find a good homography "
            f"(best had {best_inlier_count} inliers, needed >= {min_inliers}). "
            f"The images likely do not overlap enough."
        )

    log(f"RANSAC: best sample had {best_inlier_count}/{n} inliers "
        f"({100 * best_inlier_count / n:.1f}%)")

    # Step 5: refit using ALL inliers of the winning model for a more
    # accurate final homography (4 points alone are noise-sensitive).
    refined_H = compute_homography_dlt(points_a[best_inlier_mask], points_b[best_inlier_mask])

    # Recompute the inlier mask against the refined homography.
    final_errors = reprojection_error(refined_H, points_a, points_b)
    final_inlier_mask = final_errors < inlier_threshold
    log(f"After refinement: {int(np.sum(final_inlier_mask))}/{n} inliers, "
        f"mean reprojection error = {final_errors[final_inlier_mask].mean():.3f}px")

    return refined_H, final_inlier_mask
