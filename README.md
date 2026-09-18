# Panorama Stitching from Scratch

A command-line panorama stitching pipeline built for **CSE3010 - Computer Vision**
(Module 2: Depth Estimation and Multi-Camera Views). Given a folder of overlapping
photos, it stitches them into a single seamless panorama using SIFT feature
detection, feature matching, a **from-scratch RANSAC + Direct Linear Transform (DLT)
homography estimator**, perspective warping, and distance-weighted blending.

## Overview

Stitching a panorama requires figuring out the geometric transformation between
overlapping photos and merging them without visible seams. This project implements
every stage of that pipeline manually - including RANSAC and DLT, rather than
calling `cv2.findHomography()` - to demonstrate the underlying multi-view geometry
covered in the course.

## Features

- **Feature Detection** - SIFT keypoints and 128-dim descriptors (`src/feature_detection.py`)
- **Feature Matching** - brute-force matching with Lowe's ratio test (`src/feature_matching.py`)
- **Homography Estimation** - normalized Direct Linear Transform, implemented from
  scratch with SVD (`src/homography.py`)
- **Robust Estimation** - custom RANSAC loop for outlier rejection, implemented from
  scratch (`src/ransac.py`)
- **Warping** - canvas computation and perspective warping (`src/warping.py`)
- **Blending** - distance-transform feathered blending to remove seams (`src/blending.py`)
- **CLI** - runs entirely from the terminal, no GUI required (`main.py`)
- **Unit tests** - validate DLT and RANSAC against known ground-truth homographies (`tests/`)

## Technologies / Tools Used

- Python 3.10+
- OpenCV (`opencv-python`) - used only for I/O, SIFT descriptor extraction, and
  `warpPerspective`/`perspectiveTransform`; the homography math itself (DLT, RANSAC)
  is implemented from scratch in NumPy
- NumPy - linear algebra (SVD-based DLT solver)
- Matplotlib - optional plotting/visualization
- pytest - unit testing
- reportlab (Python) and docx.js (Node) - used only to generate the project report
  (PDF and DOCX), not part of the stitching pipeline itself

## Project Structure

```
panorama-stitching/
├── main.py                     # CLI entry point
├── generate_report.py          # Builds the PDF report (reportlab)
├── generate_report_docx.js     # Builds the DOCX report (docx.js)
├── package.json / package-lock.json   # Node deps for the DOCX report script
├── requirements.txt
├── statement.md                 # Problem statement, scope, target users
├── README.md
├── src/
│   ├── utils.py                 # Image I/O, logging, error handling
│   ├── feature_detection.py     # SIFT keypoint/descriptor extraction
│   ├── feature_matching.py      # Descriptor matching + Lowe's ratio test
│   ├── homography.py            # Normalized DLT homography estimation
│   ├── ransac.py                 # Custom RANSAC for outlier rejection
│   ├── warping.py                # Canvas sizing + perspective warping
│   ├── blending.py               # Distance-weighted feather blending
│   └── stitcher.py               # Orchestrates the full pipeline
├── tests/
│   ├── test_homography.py        # DLT correctness tests
│   └── test_ransac.py            # RANSAC robustness tests
├── data/
│   ├── sample/                   # Input images (synthetic + real boat set)
│   └── output/                   # Stitched panoramas are saved here
└── docs/
    ├── Project_Report.pdf / .docx   # Full project report
    ├── diagrams/                    # Architecture, workflow, UML diagrams
    ├── input_photos/                # Real input photos used in the report
    ├── independent_test/            # Second-machine reproduction screenshots
    └── *.jpg / *.png                # Keypoint, matching, and result screenshots
```

## Setup & Installation

This section walks through setup from a completely clean machine. Commands are
given for Windows (Command Prompt), macOS, and Linux where they differ.

### Step 1: Check prerequisites

You need **Python 3.10 or newer** and **pip** (Python's package installer, which
comes bundled with Python). Verify what you have:

```bash
python --version
```

On some systems (notably Windows, if the plain `python` command is not recognized,
or if it conflicts with the Microsoft Store's Python alias) use the `py` launcher
instead:

```bash
py --version
```

On macOS/Linux, if `python` points to an old Python 2 install, use `python3`:

```bash
python3 --version
```

Any of these should print `Python 3.10.x` or higher. If Python is not installed at
all, download it from [python.org/downloads](https://www.python.org/downloads/)
and make sure to check **"Add Python to PATH"** during installation on Windows.

Also confirm `pip` is available:

```bash
pip --version
```

If that fails but Python itself works, use `python -m pip --version` (or
`py -m pip --version` / `python3 -m pip --version`) instead - `pip` is then
available as a module even if it is not on your PATH directly.

### Step 2: Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

If you do not have Git installed, you can instead download the repository as a
ZIP from GitHub ("Code" -> "Download ZIP"), extract it, and open a terminal
inside the extracted folder.

### Step 3: Create a virtual environment (strongly recommended)

A virtual environment keeps this project's Python packages isolated from every
other project on your machine, so installing `opencv-python` here cannot break
or be broken by some other project's dependencies.

**Windows (Command Prompt):**
```cmd
py -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
py -m venv venv
venv\Scripts\Activate.ps1
```
If PowerShell blocks the activation script with an "execution of scripts is
disabled" error, either use Command Prompt instead, or run PowerShell as
Administrator once and execute
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then retry.

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Once activated, your terminal prompt should be prefixed with `(venv)`. Every
command below assumes the virtual environment is active.

> **Windows-specific gotcha:** once the virtual environment is active, use the
> plain `python` command (not `py`) to run scripts. The `py` launcher bypasses
> the active virtual environment entirely and can fail with a confusing
> "system cannot find the path specified" error, or silently run the wrong
> Python installation.

### Step 4: Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

This installs OpenCV, NumPy, Matplotlib, and pytest. It may take one to two
minutes and print a large amount of download/build output - that is normal.
It should end with a line similar to `Successfully installed ...`.

On Linux, if `pip install` refuses to run outside a virtual environment with an
"externally-managed-environment" error, either make sure your virtual
environment is actually activated (Step 3), or add the `--break-system-packages`
flag as a last resort:
```bash
pip install -r requirements.txt --break-system-packages
```

### Step 5: Verify the installation

```bash
python -c "import cv2, numpy; print('OpenCV:', cv2.__version__); print('NumPy:', numpy.__version__)"
```

This should print version numbers with no errors. If it fails with
`ModuleNotFoundError`, double-check that your virtual environment is active
(you should see `(venv)` in your prompt) and that Step 4 completed successfully.

### Step 6: Run the unit tests (optional but recommended)

```bash
python -m pytest tests/ -v
```

You should see 4 tests, all `PASSED`. This confirms the core homography/RANSAC
math is working correctly on your machine before you run the full pipeline.

You are now ready to run the stitcher - see **Usage** below.

## Usage

Place 2 or more overlapping images (in left-to-right order, named so they sort
correctly, e.g. `img_01.jpg`, `img_02.jpg`, `img_03.jpg`) into a folder, then run:

```bash
python main.py --input data/sample --output data/output/panorama.jpg
```

### Arguments

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Folder containing 2+ overlapping input images |
| `--output` | `-o` | No (default: `data/output/panorama.jpg`) | Path to save the resulting panorama |

### Example

```bash
python main.py --input data/sample --output data/output/my_panorama.jpg
```

Expected console output includes progress logs for each pipeline stage
(feature detection counts, match counts, RANSAC inlier ratio, etc.) and ends
with `Saved result to ...` on success.

## Testing

Unit tests validate the DLT and RANSAC implementations against synthetic,
ground-truth homographies (no real images required):

```bash
python -m pytest tests/ -v
```

## Notes on Input Images

- Images should overlap by roughly 25-50%.
- Images should be taken from (approximately) the same viewpoint, rotating the
  camera rather than translating it sideways, for best results (this matches the
  planar/rotational assumption behind a 2D homography).
- Low-texture images (e.g. a plain wall) will fail feature detection - this is
  a fundamental limitation of feature-based methods, not a bug.

## Future Enhancements

- Multi-band (Laplacian pyramid) blending instead of simple feathering
- Automatic image ordering instead of assuming filename sort order
- Bundle adjustment for stitching many images with reduced drift
- Cylindrical/spherical projection for very wide (360 degree) panoramas
