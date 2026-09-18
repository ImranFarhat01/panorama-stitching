"""
warping.py
----------
Module 4 of the pipeline: WARPING.

Once we have a homography H mapping image B's plane onto image A's
plane, we need to:
  1. Figure out how big the combined output canvas must be (image B's
     corners land somewhere outside image A's original frame after
     being transformed, usually to the side).
  2. Warp image B into that canvas using H (cv2.warpPerspective).
  3. Place image A into the same canvas (with a translation offset,
     since the canvas may extend to the left/above image A's origin).
"""

import cv2
import numpy as np


def compute_canvas(image_a: np.ndarray, image_b: np.ndarray, H: np.ndarray):
    """Compute the output canvas size and the translation needed so that
    all warped content has non-negative coordinates.

    Returns
    -------
    canvas_size : (width, height)
    translation : np.ndarray, shape (3, 3)
        A translation homography to shift everything into positive space.
    """
    h_a, w_a = image_a.shape[:2]
    h_b, w_b = image_b.shape[:2]

    # Corners of image A (fixed, identity transform).
    corners_a = np.float32([[0, 0], [w_a, 0], [w_a, h_a], [0, h_a]]).reshape(-1, 1, 2)

    # Corners of image B, projected through H into image A's frame.
    corners_b = np.float32([[0, 0], [w_b, 0], [w_b, h_b], [0, h_b]]).reshape(-1, 1, 2)
    warped_corners_b = cv2.perspectiveTransform(corners_b, H)

    all_corners = np.concatenate([corners_a, warped_corners_b], axis=0)
    x_min, y_min = np.floor(all_corners.min(axis=0).ravel()).astype(int)
    x_max, y_max = np.ceil(all_corners.max(axis=0).ravel()).astype(int)

    translation = np.array([
        [1, 0, -x_min],
        [0, 1, -y_min],
        [0, 0, 1],
    ], dtype=np.float64)

    canvas_size = (x_max - x_min, y_max - y_min)
    return canvas_size, translation


def warp_image(image: np.ndarray, H: np.ndarray, canvas_size) -> np.ndarray:
    """Warp `image` through homography H into a canvas of the given size."""
    return cv2.warpPerspective(image, H, canvas_size)
