# Problem Statement

## Problem Statement

Combining multiple overlapping photographs of a scene into a single, wide,
seamless panoramic image requires solving several classic computer vision
problems: detecting distinctive image features, matching those features across
views, robustly estimating the geometric transformation (homography) that
relates the different camera viewpoints in the presence of noisy/incorrect
matches, and blending the aligned images without visible seams. This project
implements a complete panorama stitching pipeline that solves each of these
sub-problems from first principles, directly applying the multi-camera view
geometry concepts (homography, DLT, RANSAC) covered in CSE3010 Module 2.

## Scope

The project covers:
- Feature detection and description (SIFT)
- Feature matching with outlier filtering (ratio test)
- Homography estimation via normalized Direct Linear Transform (from scratch)
- Robust estimation via RANSAC (from scratch, not `cv2.findHomography`)
- Perspective warping and canvas composition
- Seam removal via distance-weighted feather blending
- A command-line interface for end-to-end execution
- Unit tests validating the homography/RANSAC math against synthetic ground truth

Out of scope (noted under Future Enhancements in the README):
- Automatic detection of image order/adjacency (images must be supplied in order)
- Multi-band/Laplacian pyramid blending
- Cylindrical or spherical projection for full 360° panoramas
- Bundle adjustment / global optimization across many images

## Target Users

- Students and instructors studying multi-view geometry and homography
  estimation, as a transparent, dependency-light reference implementation
- Anyone wanting to stitch a small set of overlapping photos into a panorama
  from the command line without a phone app or GUI tool

## High-Level Features

1. **Feature Detection Module** — extracts SIFT keypoints and descriptors from
   each input image.
2. **Feature Matching Module** — matches descriptors between image pairs using
   brute-force nearest-neighbor search with Lowe's ratio test.
3. **Homography + RANSAC Module** — robustly estimates the transformation
   between each image pair, rejecting outlier matches, using a from-scratch
   normalized DLT solver and RANSAC loop.
4. **Warping & Blending Module** — warps images into a shared canvas and blends
   overlapping regions seamlessly using distance-transform feathering.
5. **CLI Pipeline** — orchestrates all modules end-to-end via a single terminal
   command, with progress logging and error handling at every stage.
