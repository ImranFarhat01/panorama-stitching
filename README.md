# Panorama Stitching from Scratch

A command-line panorama stitching pipeline built for **CSE3010 – Computer Vision**
(Module 2: Depth Estimation and Multi-Camera Views). Given a folder of overlapping
photos, it stitches them into a single seamless panorama using SIFT feature
detection, feature matching, a **from-scratch RANSAC + Direct Linear Transform (DLT)
homography estimator**, perspective warping, and distance-weighted blending.

## Overview

Stitching a panorama requires figuring out the geometric transformation between
overlapping photos and merging them without visible seams. This project implements
every stage of that pipeline manually — including RANSAC and DLT, rather than
calling `cv2.findHomography()` — to demonstrate the underlying multi-view geometry
covered in the course.

## Features

- **Feature Detection** — SIFT keypoints and 128-dim descriptors (`src/feature_detection.py`)
- **Feature Matching** — brute-force matching with Lowe's ratio test (`src/feature_matching.py`)
- **Homography Estimation** — normalized Direct Linear Transform, implemented from
  scratch with SVD (`src/homography.py`)
- **Robust Estimation** — custom RANSAC loop for outlier rejection, implemented from
  scratch (`src/ransac.py`)
- **Warping** — canvas computation and perspective warping (`src/warping.py`)
- **Blending** — distance-transform feathered blending to remove seams (`src/blending.py`)
- **CLI** — runs entirely from the terminal, no GUI required (`main.py`)
- **Unit tests** — validate DLT and RANSAC against known ground-truth homographies (`tests/`)

## Technologies / Tools Used

- Python 3.10+
- OpenCV (`opencv-python`) — used only for I/O, SIFT descriptor extraction, and
  `warpPerspective`/`perspectiveTransform`; the homography math itself (DLT, RANSAC)
  is implemented from scratch in NumPy
- NumPy — linear algebra (SVD-based DLT solver)
- Matplotlib — optional plotting/visualization
- pytest — unit testing

## Project Structure

```
panorama-stitching/
├── main.py                    # CLI entry point
├── requirements.txt
├── statement.md                # Problem statement, scope, target users
├── README.md
├── src/
│   ├── utils.py                # Image I/O, logging, error handling
│   ├── feature_detection.py    # SIFT keypoint/descriptor extraction
│   ├── feature_matching.py     # Descriptor matching + Lowe's ratio test
│   ├── homography.py           # Normalized DLT homography estimation
│   ├── ransac.py                # Custom RANSAC for outlier rejection
│   ├── warping.py               # Canvas sizing + perspective warping
│   ├── blending.py              # Distance-weighted feather blending
│   └── stitcher.py              # Orchestrates the full pipeline
├── tests/
│   ├── test_homography.py       # DLT correctness tests
│   └── test_ransac.py           # RANSAC robustness tests
├── data/
│   ├── sample/                  # Put your input images here
│   └── output/                  # Stitched panoramas are saved here
└── docs/                        # Architecture notes, report screenshots
```

## Setup & Installation

### 1. Prerequisites
- Python 3.10 or newer
- pip

### 2. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 3. (Recommended) Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

Place 2 or more overlapping images (in left-to-right order, named so they sort
correctly, e.g. `img_01.jpg`, `img_02.jpg`, `img_03.jpg`) into a folder, then run:

```bash
python3 main.py --input data/sample --output data/output/panorama.jpg
```

### Arguments

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Folder containing 2+ overlapping input images |
| `--output` | `-o` | No (default: `data/output/panorama.jpg`) | Path to save the resulting panorama |

### Example

```bash
python3 main.py --input data/sample --output data/output/my_panorama.jpg
```

Expected console output includes progress logs for each pipeline stage
(feature detection counts, match counts, RANSAC inlier ratio, etc.) and ends
with `Saved result to ...` on success.

## Testing

Unit tests validate the DLT and RANSAC implementations against synthetic,
ground-truth homographies (no real images required):

```bash
python3 -m pytest tests/ -v
```

## Notes on Input Images

- Images should overlap by roughly 25–50%.
- Images should be taken from (approximately) the same viewpoint, rotating the
  camera rather than translating it sideways, for best results (this matches the
  planar/rotational assumption behind a 2D homography).
- Low-texture images (e.g. a plain wall) will fail feature detection — this is
  a fundamental limitation of feature-based methods, not a bug.

## Future Enhancements

- Multi-band (Laplacian pyramid) blending instead of simple feathering
- Automatic image ordering instead of assuming filename sort order
- Bundle adjustment for stitching many images with reduced drift
- Cylindrical/spherical projection for very wide (360°) panoramas
