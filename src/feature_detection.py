"""
feature_detection.py
---------------------
Module 1 of the pipeline: FEATURE DETECTION.

Goal: find distinctive, repeatable points in an image (corners, blobs,
textured regions) that we can reliably find again in an overlapping
photo of the same scene, even if that photo is rotated, scaled, or has
different lighting.

We use SIFT (Scale-Invariant Feature Transform):
  - It detects "keypoints": (x, y) locations + scale + orientation.
  - For each keypoint, it computes a "descriptor": a 128-number vector
    that describes the local image patch around that point in a way
    that is invariant to scale and rotation. Two keypoints from
    different images that show the same physical spot will have
    very similar descriptors.

This directly implements Module 2 syllabus content: feature-based
registration for multi-camera views.
"""

import cv2
import numpy as np
from src.utils import to_gray, log


def detect_features(image: np.ndarray, max_features: int = 4000):
    """Detect SIFT keypoints and compute their descriptors.

    Parameters
    ----------
    image : np.ndarray
        BGR image (as loaded by OpenCV).
    max_features : int
        Cap on the number of keypoints kept (best-scoring ones are kept),
        which bounds runtime for large/high-resolution images.

    Returns
    -------
    keypoints : list[cv2.KeyPoint]
        Detected keypoint locations.
    descriptors : np.ndarray, shape (N, 128)
        One 128-dim descriptor vector per keypoint.
    """
    gray = to_gray(image)

    # nfeatures=0 means "no cap inside SIFT itself"; we cap manually
    # below so behavior is explicit and testable.
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    if descriptors is None or len(keypoints) == 0:
        raise RuntimeError(
            "No features detected. The image may be blank, too small, "
            "or too low-contrast for SIFT to find keypoints."
        )

    if len(keypoints) > max_features:
        # Keep the strongest keypoints by response score.
        order = np.argsort([-kp.response for kp in keypoints])[:max_features]
        keypoints = [keypoints[i] for i in order]
        descriptors = descriptors[order]

    log(f"Detected {len(keypoints)} keypoints")
    return keypoints, descriptors


def draw_keypoints(image: np.ndarray, keypoints) -> np.ndarray:
    """Return a copy of the image with keypoints drawn on it (for report screenshots)."""
    return cv2.drawKeypoints(
        image,
        keypoints,
        None,
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )
