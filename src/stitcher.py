"""
stitcher.py
-----------
Module 6: THE STITCHER — orchestrates modules 1-5 into a working pipeline.

Given a list of images (in left-to-right order), stitches them into a
single panorama by processing pairs sequentially: stitch image[0] and
image[1] into a partial panorama, then stitch that result with
image[2], and so on. This keeps the pipeline simple (only ever needs
pairwise homography estimation) while still supporting any number of
input images.
"""

import numpy as np
from src.feature_detection import detect_features
from src.feature_matching import match_features, get_matched_points
from src.ransac import ransac_homography
from src.warping import compute_canvas, warp_image
from src.blending import feather_blend
from src.utils import log


def stitch_pair(image_a: np.ndarray, image_b: np.ndarray) -> np.ndarray:
    """Stitch two overlapping images into one panorama.

    image_a is treated as the fixed reference frame; image_b is
    detected, matched against image_a, and warped to align with it.
    """
    log("Detecting features in image A...")
    kp_a, desc_a = detect_features(image_a)
    log("Detecting features in image B...")
    kp_b, desc_b = detect_features(image_b)

    log("Matching features...")
    matches = match_features(desc_a, desc_b)
    points_a, points_b = get_matched_points(kp_a, kp_b, matches)

    log("Estimating homography with RANSAC...")
    # We want H that maps image_b -> image_a's frame, so points_b are
    # the "source" and points_a are the "destination" in our DLT
    # convention (see homography.py's docstring).
    H, inlier_mask = ransac_homography(points_a, points_b)

    log("Computing output canvas...")
    canvas_size, translation = compute_canvas(image_a, image_b, H)

    log("Warping images into shared canvas...")
    warped_b = warp_image(image_b, translation @ H, canvas_size)
    warped_a = warp_image(image_a, translation, canvas_size)

    log("Blending...")
    result = feather_blend(warped_a, warped_b)

    return result


def crop_black_borders(image: np.ndarray) -> np.ndarray:
    """Crop away the black border left around the panorama after warping.

    Purely cosmetic, but makes the final output look like a real
    panorama photo rather than a photo on a black canvas.
    """
    gray_sum = image.sum(axis=2)
    rows = np.where(gray_sum.sum(axis=1) > 0)[0]
    cols = np.where(gray_sum.sum(axis=0) > 0)[0]
    if len(rows) == 0 or len(cols) == 0:
        return image
    return image[rows.min():rows.max() + 1, cols.min():cols.max() + 1]


def stitch_images(images: list) -> np.ndarray:
    """Stitch a list of >= 2 images (in order) into one panorama."""
    if len(images) < 2:
        raise ValueError("Need at least 2 images to stitch a panorama")

    panorama = images[0]
    for i in range(1, len(images)):
        log(f"--- Stitching image {i + 1}/{len(images)} onto panorama ---")
        panorama = stitch_pair(panorama, images[i])

    return crop_black_borders(panorama)
