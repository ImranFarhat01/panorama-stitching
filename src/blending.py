"""
blending.py
-----------
Module 5 of the pipeline: BLENDING.

Once both images are warped into the same canvas, simply overlaying
them produces a visible seam where they overlap (brightness/exposure
differences between the two photos become obvious). We fix this with
FEATHERING (alpha blending weighted by distance from each image's
edge):

  - For each warped image, compute a "distance map": every pixel's
    distance to the nearest black/empty border of that image.
  - In the overlap region, blend the two images using weights
    proportional to each pixel's distance value: pixels deep inside
    an image (far from its edge) are trusted more than pixels near
    its edge, where warping artifacts are most visible.
  - Outside the overlap, just keep whichever image has valid pixels.
"""

import cv2
import numpy as np


def _distance_weight(image: np.ndarray) -> np.ndarray:
    """Distance transform of the non-black region of `image`, normalized to [0, 1]."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = (gray > 0).astype(np.uint8)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    max_val = dist.max()
    if max_val > 0:
        dist = dist / max_val
    return dist


def feather_blend(canvas_a: np.ndarray, canvas_b: np.ndarray) -> np.ndarray:
    """Blend two same-size warped images using distance-weighted feathering.

    Both inputs are expected to be on the same canvas: black (0,0,0)
    pixels represent "no data" from that source.
    """
    weight_a = _distance_weight(canvas_a)
    weight_b = _distance_weight(canvas_b)

    total_weight = weight_a + weight_b
    # Avoid division by zero where neither image has data.
    total_weight_safe = np.where(total_weight == 0, 1, total_weight)

    norm_a = (weight_a / total_weight_safe)[..., None]
    norm_b = (weight_b / total_weight_safe)[..., None]

    blended = (canvas_a.astype(np.float64) * norm_a +
               canvas_b.astype(np.float64) * norm_b)

    return np.clip(blended, 0, 255).astype(np.uint8)
