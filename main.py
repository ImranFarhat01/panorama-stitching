#!/usr/bin/env python3
"""
main.py
-------
Command-line entry point for the Panorama Stitching pipeline.

Usage:
    python3 main.py --input data/sample --output data/output/panorama.jpg

The project runs entirely from the terminal, no GUI required, per the
submission's "Project Executability" requirement.
"""

import argparse
import time
from src.utils import load_images_from_folder, save_image, log, error
from src.stitcher import stitch_images


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stitch a folder of overlapping images into a panorama "
                    "using SIFT features, custom RANSAC, and homography warping."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to a folder containing 2+ overlapping images, in left-to-right order."
    )
    parser.add_argument(
        "--output", "-o", default="data/output/panorama.jpg",
        help="Path to save the resulting panorama image."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    log("=== Panorama Stitching Pipeline ===")
    start_time = time.time()

    try:
        images = load_images_from_folder(args.input)
        panorama = stitch_images(images)
        save_image(args.output, panorama)
    except Exception as exc:
        error(f"Pipeline failed: {exc}")

    elapsed = time.time() - start_time
    log(f"Done in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    main()
