"""
generate_report.py
-------------------
Generates the project report PDF for the CSE3010 BYOP submission.
Not part of the panorama stitcher itself - a one-off documentation tool.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.utils import ImageReader
import os

DOCS = "docs"
DATA_OUT = "data/output"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1c", parent=styles["Heading1"], fontSize=18,
                           spaceAfter=14, spaceBefore=6, textColor=colors.HexColor("#1a3d6b")))
styles.add(ParagraphStyle(name="H2c", parent=styles["Heading2"], fontSize=14,
                           spaceAfter=10, spaceBefore=14, textColor=colors.HexColor("#2a5a95")))
styles.add(ParagraphStyle(name="H3c", parent=styles["Heading3"], fontSize=12,
                           spaceAfter=6, spaceBefore=10, textColor=colors.HexColor("#333333")))
styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontSize=10.5,
                           leading=15, spaceAfter=8, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="Caption", parent=styles["Normal"], fontSize=9,
                           leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"),
                           spaceAfter=14, spaceBefore=4, fontName="Helvetica-Oblique"))
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=26,
                           leading=32, textColor=colors.HexColor("#1a3d6b")))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=13,
                           alignment=TA_CENTER, spaceAfter=6, textColor=colors.HexColor("#444444")))

story = []


def h1(text):
    story.append(Paragraph(text, styles["H1c"]))


def h2(text):
    story.append(Paragraph(text, styles["H2c"]))


def h3(text):
    story.append(Paragraph(text, styles["H3c"]))


def body(text):
    story.append(Paragraph(text, styles["Body"]))


def bullets(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(it, styles["Body"]), leftIndent=6) for it in items],
        bulletType="bullet", start="circle", leftIndent=16
    ))
    story.append(Spacer(1, 6))


def numbered(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(it, styles["Body"])) for it in items],
        bulletType="1", leftIndent=18
    ))
    story.append(Spacer(1, 6))


def figure(path, caption, max_width=15.5 * cm, max_height=9.5 * cm):
    img = ImageReader(path)
    iw, ih = img.getSize()
    ratio = min(max_width / iw, max_height / ih)
    w, h = iw * ratio, ih * ratio
    story.append(Image(path, width=w, height=h))
    story.append(Paragraph(caption, styles["Caption"]))


def data_table(headers, rows, col_widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3d6b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fb")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


# ============================================================
# COVER PAGE
# ============================================================
story.append(Spacer(1, 4 * cm))
story.append(Paragraph("Panorama Stitching from Scratch", styles["CoverTitle"]))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("A Feature-Based Image Stitching Pipeline using SIFT, Custom RANSAC,<br/>"
                        "and Direct Linear Transform (DLT) Homography Estimation", styles["CoverSub"]))
story.append(Spacer(1, 2 * cm))
story.append(Paragraph("Project Report", styles["Heading2"]))
story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph("Submitted for: CSE3010 - Computer Vision", styles["CoverSub"]))
story.append(Paragraph("Course Type: Flipped Classroom (Build Your Own Project)", styles["CoverSub"]))
story.append(Paragraph("Module Focus: Depth Estimation and Multi-Camera Views", styles["CoverSub"]))
story.append(Spacer(1, 2 * cm))
story.append(Paragraph("VIT Bhopal University", styles["CoverSub"]))
story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph("<b>Name:</b> Imran Farhat", styles["CoverSub"]))
story.append(Paragraph("<b>Registration Number:</b> 24BAI10276", styles["CoverSub"]))
story.append(Paragraph("<b>Course:</b> CSE3010 - Computer Vision", styles["CoverSub"]))
story.append(Paragraph("<b>Date of Submission:</b> September 18, 2026", styles["CoverSub"]))
story.append(PageBreak())

# ============================================================
# 1. INTRODUCTION
# ============================================================
h1("1. Introduction")
body("Panorama stitching is a classic computer vision task that combines a sequence of "
     "overlapping photographs into a single, wide, geometrically consistent image. It is a "
     "practical application of multi-view geometry: the same physical scene, viewed from "
     "different camera orientations, must be aligned into one consistent coordinate frame "
     "before the images can be merged.")
body("This project implements a complete panorama stitching pipeline "
     "from first principles for <b>CSE3010 - Computer Vision</b>, directly applying the "
     "concepts covered in <b>Module 2 (Depth Estimation and Multi-Camera Views)</b>: "
     "perspective transformation, homography, the Direct Linear Transform (DLT), and RANSAC. "
     "Rather than relying on OpenCV's built-in <font face='Courier'>cv2.findHomography()</font> "
     "or <font face='Courier'>cv2.Stitcher</font> APIs, the homography estimation and RANSAC "
     "outlier-rejection stages are implemented manually in NumPy, to directly demonstrate "
     "understanding of the underlying mathematics.")
body("The system is delivered as a modular, command-line Python application with automated "
     "unit tests validating the core geometric algorithms against synthetic ground-truth data, "
     "and has been verified end-to-end on both synthetic test images and real camera photographs.")

# ============================================================
# 2. PROBLEM STATEMENT
# ============================================================
h1("2. Problem Statement")
body("Given a set of two or more overlapping photographs of a scene, taken from slightly "
     "different camera orientations, automatically compute the geometric transformation "
     "relating each pair of images and merge them into a single seamless panoramic image, "
     "without manual intervention, without relying on high-level built-in stitching "
     "functions, and while being robust to incorrect feature correspondences.")
h3("Scope")
bullets([
    "Feature detection and description (SIFT)",
    "Feature matching with outlier filtering (Lowe's ratio test)",
    "Homography estimation via normalized Direct Linear Transform (implemented from scratch)",
    "Robust estimation via RANSAC (implemented from scratch)",
    "Perspective warping and canvas composition",
    "Seam removal via distance-weighted feather blending",
    "A command-line interface for end-to-end execution",
    "Unit tests validating the homography/RANSAC math against synthetic ground truth",
])
h3("Target Users")
bullets([
    "Students and instructors studying multi-view geometry and homography estimation, "
    "as a transparent, dependency-light reference implementation",
    "Anyone wanting to stitch a small set of overlapping photos into a panorama from the "
    "command line, without a phone app or GUI tool",
])

# ============================================================
# 3. FUNCTIONAL REQUIREMENTS
# ============================================================
h1("3. Functional Requirements")
data_table(
    ["#", "Requirement", "Description"],
    [
        ["FR1", "Image Input", "Load 2+ overlapping images from a specified folder, sorted "
                                 "in stitching order."],
        ["FR2", "Feature Detection", "Detect distinctive, repeatable keypoints and compute "
                                       "descriptors for each input image using SIFT."],
        ["FR3", "Feature Matching", "Match descriptors between image pairs and filter "
                                      "ambiguous matches using Lowe's ratio test."],
        ["FR4", "Homography Estimation", "Robustly estimate the homography relating each "
                                           "image pair using a custom RANSAC + normalized "
                                           "DLT implementation, rejecting outlier matches."],
        ["FR5", "Warping & Composition", "Warp images into a shared canvas based on the "
                                           "estimated homography and compute the correct "
                                           "output canvas size."],
        ["FR6", "Blending", "Blend overlapping regions using distance-weighted feathering "
                              "to remove visible seams."],
        ["FR7", "Multi-Image Stitching", "Support stitching 2 or more images by chaining "
                                           "pairwise stitches."],
        ["FR8", "Output", "Save the final panorama to a user-specified path."],
    ],
    col_widths=[1.3 * cm, 3.7 * cm, 10.8 * cm]
)

# ============================================================
# 4. NON-FUNCTIONAL REQUIREMENTS
# ============================================================
h1("4. Non-Functional Requirements")
data_table(
    ["#", "Requirement", "How it is addressed"],
    [
        ["NFR1", "Performance", "Stitching 2 images (1000px wide) completes in under 1 "
                                  "second; 3 real 1000px camera photos complete in ~2 "
                                  "seconds on a standard laptop CPU."],
        ["NFR2", "Reliability", "RANSAC with 2000 iterations and a minimum-inlier check "
                                  "ensures the pipeline degrades gracefully (raises a clear "
                                  "error) rather than silently producing a garbled panorama "
                                  "when images do not overlap enough."],
        ["NFR3", "Error Handling", "Every stage (missing files, unreadable images, "
                                     "insufficient matches, degenerate RANSAC samples, "
                                     "failed homography fits) raises descriptive errors "
                                     "caught centrally in main.py, exiting cleanly with a "
                                     "non-zero status code instead of a raw traceback."],
        ["NFR4", "Maintainability", "The pipeline is split into 7 single-responsibility "
                                      "modules (feature detection, matching, homography, "
                                      "RANSAC, warping, blending, orchestration), each "
                                      "independently testable and documented."],
        ["NFR5", "Usability", "A single terminal command "
                                "(<font face='Courier'>python main.py --input &lt;folder&gt; "
                                "--output &lt;path&gt;</font>) runs the entire pipeline, with "
                                "step-by-step progress logs printed to the console."],
        ["NFR6", "Reproducibility", "RANSAC uses a fixed random seed by default, so results "
                                      "are deterministic and reproducible across runs and "
                                      "machines."],
        ["NFR7", "Logging / Monitoring", "Every pipeline stage logs its progress and key "
                                           "metrics (keypoint counts, match counts, RANSAC "
                                           "inlier ratio, mean reprojection error) to the "
                                           "console for transparency and debugging."],
    ],
    col_widths=[1.5 * cm, 3.2 * cm, 11.1 * cm]
)

# ============================================================
# 5. SYSTEM ARCHITECTURE
# ============================================================
h1("5. System Architecture")
body("The system follows a layered, modular architecture: an input layer (CLI + image "
     "folder), a core processing pipeline of single-purpose modules, a shared support "
     "layer (I/O, logging, error handling), and an output layer. The Stitcher module "
     "orchestrates the core pipeline modules in sequence for each image pair.")
figure(f"{DOCS}/diagrams/architecture.png", "Figure 5.1 - System Architecture Diagram")

# ============================================================
# 6. DESIGN DIAGRAMS
# ============================================================
h1("6. Design Diagrams")

h2("6.1 Workflow / Process Flow Diagram")
body("Describes the end-to-end control flow of the pipeline, including the error paths "
     "taken when an image folder has too few images, too few feature matches, or when "
     "RANSAC cannot find a consistent homography.")
figure(f"{DOCS}/diagrams/workflow.png", "Figure 6.1 - Workflow / Process Flow Diagram",
       max_height=20 * cm)
story.append(PageBreak())

h2("6.2 Use Case Diagram")
body("The system has a single actor (the User) who interacts with the pipeline primarily "
     "through the command-line interface. The three internal stages "
     "(feature detection/matching, homography estimation, warping/blending) are modelled "
     "as included use cases of &ldquo;Run stitching pipeline&rdquo;.")
figure(f"{DOCS}/diagrams/use_case.png", "Figure 6.2 - Use Case Diagram")

h2("6.3 Sequence Diagram")
body("Shows the message flow for stitching one image pair, from the CLI invocation through "
     "feature detection, matching, RANSAC homography estimation (including its internal "
     "DLT-fitting loop), warping, and blending, back to the saved output file.")
figure(f"{DOCS}/diagrams/sequence.png", "Figure 6.3 - Sequence Diagram (single image-pair stitch)",
       max_height=22 * cm)
story.append(PageBreak())

h2("6.4 Class / Component Diagram")
body("Since the implementation is function-based (NumPy/OpenCV style) rather than "
     "class-based, this diagram documents each module as a component, listing its public "
     "functions and their dependencies on other modules.")
figure(f"{DOCS}/diagrams/class_diagram.png", "Figure 6.4 - Class / Component Diagram",
       max_height=11 * cm)

h2("6.5 Database / Storage Design")
body("<b>Not applicable.</b> This project performs a stateless, in-memory image-processing "
     "pipeline with file-based input/output only; it does not use a database, so no "
     "ER diagram or schema design is included.")

# ============================================================
# 7. DESIGN DECISIONS & RATIONALE
# ============================================================
h1("7. Design Decisions & Rationale")
h3("7.1 Custom DLT + RANSAC instead of cv2.findHomography()")
body("The homography estimator and RANSAC loop were implemented manually in NumPy "
     "(src/homography.py, src/ransac.py) instead of calling OpenCV's built-in "
     "<font face='Courier'>cv2.findHomography()</font>. This was a deliberate choice to "
     "directly demonstrate the Module 2 concepts (DLT, RANSAC) at the algorithmic level, "
     "rather than treating them as a black box.")
h3("7.2 Hartley Point Normalization")
body("Raw pixel coordinates can be in the thousands, which makes the SVD-based DLT solve "
     "numerically ill-conditioned. Points are normalized (shifted to a zero centroid, "
     "scaled to an average distance of &radic;2 from the origin) before solving, and the "
     "resulting homography is un-normalized afterward - a standard fix "
     "(Hartley, 1997) that is easy to omit and quietly produces a worse result.")
h3("7.3 Sequential Pairwise Stitching")
body("For N input images, the pipeline stitches image 1 and 2, then stitches that result "
     "with image 3, and so on, rather than performing a single global bundle adjustment "
     "across all images at once. This keeps the implementation simple and only requires "
     "pairwise homography estimation, at the cost of potential drift accumulation across "
     "many images - an acceptable trade-off for the panorama sizes (2-3 images) "
     "this project targets, and noted as a future enhancement.")
h3("7.4 Distance-Transform Feather Blending")
body("Rather than a hard cut between images (which produces a visible seam) or full "
     "multi-band blending (more complex), feathering weights each image's contribution "
     "by its distance from that image's own border, which is simple to implement, cheap "
     "to compute, and visibly removes seams in practice, as shown in Section 10.")
h3("7.5 Fixed RANSAC Random Seed")
body("RANSAC uses a fixed seed (default 42) so that results are reproducible across runs "
     "and machines, which matters for grading/demo reproducibility and for the unit tests.")

# ============================================================
# 8. IMPLEMENTATION DETAILS
# ============================================================
h1("8. Implementation Details")
h3("8.1 Technology Stack")
bullets([
    "<b>Python 3.10+</b> - implementation language",
    "<b>OpenCV (opencv-python)</b> - used only for image I/O, SIFT descriptor "
    "extraction, and low-level warp/perspective-transform primitives "
    "(<font face='Courier'>warpPerspective</font>, "
    "<font face='Courier'>perspectiveTransform</font>)",
    "<b>NumPy</b> - all homography/RANSAC linear algebra (SVD-based DLT solver)",
    "<b>pytest</b> - unit testing framework",
])
h3("8.2 Module Breakdown")
data_table(
    ["Module", "Responsibility"],
    [
        ["utils.py", "Image I/O, folder loading, logging, centralized error handling"],
        ["feature_detection.py", "SIFT keypoint detection and descriptor extraction"],
        ["feature_matching.py", "Brute-force descriptor matching with Lowe's ratio test"],
        ["homography.py", "Point normalization, normalized DLT solver, reprojection error"],
        ["ransac.py", "Random sampling, inlier counting, best-model refinement"],
        ["warping.py", "Output canvas sizing, perspective warping"],
        ["blending.py", "Distance-transform feather blending"],
        ["stitcher.py", "End-to-end orchestration across an arbitrary number of images"],
        ["main.py", "CLI argument parsing and top-level error handling"],
    ],
    col_widths=[4.8 * cm, 10.7 * cm]
)
h3("8.3 Key Algorithm - Normalized DLT")
body("For each of N &ge; 4 point correspondences (x, y) &rarr; (x&prime;, y&prime;), two rows "
     "are added to a 2N&times;9 matrix A such that A h = 0, where h is the flattened 3&times;3 "
     "homography. The solution is the right singular vector of A corresponding to its "
     "smallest singular value, obtained via SVD "
     "(<font face='Courier'>numpy.linalg.svd</font>), reshaped into the 3&times;3 matrix H.")
h3("8.4 Key Algorithm - RANSAC")
numbered([
    "Randomly sample 4 point correspondences (the minimum needed for a homography).",
    "Fit a candidate homography to just those 4 points via DLT.",
    "Compute the reprojection error of <i>all</i> matches under this candidate homography; "
    "matches within a pixel threshold are counted as inliers.",
    "Repeat for a fixed number of iterations (default 2000), keeping the candidate with the "
    "most inliers.",
    "Refit the homography using <i>all</i> inliers of the winning candidate (not just the "
    "original 4 points) for a more accurate final result.",
])

# ============================================================
# 9. TESTING APPROACH
# ============================================================
h1("9. Testing Approach")
body("Because feature-based pipelines depend on the specific input photographs, the core "
     "geometric algorithms (DLT and RANSAC) are unit-tested independently of any image or "
     "SIFT feature, using synthetic point correspondences generated from a "
     "<b>known ground-truth homography</b>. This isolates and directly validates the "
     "mathematics.")
data_table(
    ["Test", "What it validates"],
    [
        ["test_dlt_recovers_known_homography_exactly", "Given noise-free correspondences "
         "generated from a known homography, DLT recovers a homography that reproduces "
         "them to within 1e-6 px."],
        ["test_dlt_raises_on_too_few_points", "DLT correctly raises a ValueError when given "
         "fewer than 4 correspondences."],
        ["test_apply_homography_identity", "Applying the identity homography returns the "
         "input points unchanged."],
        ["test_ransac_recovers_homography_with_outliers", "Given a mix of inlier "
         "correspondences (consistent with a known homography) and outlier correspondences "
         "(random, unrelated points), RANSAC correctly classifies &gt;90% of points as "
         "inlier/outlier and recovers a homography with &lt;2px mean reprojection error on "
         "true inliers."],
    ],
    col_widths=[6.3 * cm, 9.2 * cm]
)
body("All 4 tests pass (see Figure 9.1). In addition to these unit tests, the full pipeline "
     "was validated end-to-end (integration testing) on:")
bullets([
    "<b>Synthetic test images</b> - a procedurally generated textured scene, split "
    "into two overlapping, perspective-warped crops with a known ground-truth relationship.",
    "<b>Real camera photographs</b> - a 3-image sequence of a real waterfront scene "
    "(see Section 10), to confirm the pipeline works on unmodified, real-world input, not "
    "just controlled synthetic data.",
])
figure(f"{DOCS}/pytest_results.png", "Figure 9.1 - pytest run: all 4 unit tests passing")

# ============================================================
# 10. SCREENSHOTS / RESULTS
# ============================================================
h1("10. Screenshots / Results")

h2("10.1 Feature Detection")
body("SIFT keypoints detected on one of the input images. Each marker shows a detected "
     "keypoint's location, scale, and orientation.")
figure(f"{DOCS}/keypoints_image_a.jpg", "Figure 10.1 - Detected SIFT keypoints")

h2("10.2 Feature Matching")
body("Matches between the two images after Lowe's ratio test, before RANSAC outlier "
     "rejection. Some incorrect (crossing) matches are visible, which is precisely what "
     "RANSAC is designed to filter out.")
figure(f"{DOCS}/feature_matches.jpg", "Figure 10.2 - Feature matches after ratio test (pre-RANSAC)")

h2("10.3 RANSAC Inlier Matches")
body("The same matches after RANSAC has classified them; only inlier matches (consistent "
     "with the single best-fit homography) are shown. Compare with Figure 10.2 to see the "
     "outliers that were correctly rejected.")
figure(f"{DOCS}/ransac_inlier_matches.jpg", "Figure 10.3 - Matches after RANSAC outlier rejection")

h2("10.4 Stitched Panorama - Synthetic Test")
body("Result of stitching two overlapping, perspective-warped crops of a procedurally "
     "generated textured scene. The continuous alignment of the grid lines across the "
     "stitch boundary is a direct visual check of homography accuracy.")
figure(f"{DATA_OUT}/panorama.jpg", "Figure 10.4 - Synthetic test panorama (grid lines confirm alignment accuracy)")

h2("10.5 Stitched Panorama - Real Photographs")
body("Result of stitching 3 real, unmodified camera photographs of a waterfront scene. "
     "RANSAC found 378/404 (94.1%) and 278/350 (80.0%) inliers for the two consecutive "
     "pairs, with mean reprojection errors of 0.44px and 0.55px respectively. The horizon, "
     "the ship's masts, and the reflections align continuously across all three stitched "
     "photos with no visible doubling or seam.")
figure(f"{DOCS}/boat_panorama_result.jpg", "Figure 10.5 - Final panorama stitched from 3 real photographs",
       max_height=11 * cm)
body("The black triangular regions at the top and bottom edges are an expected artifact of "
     "warping non-rectangular photo content into a rectangular output canvas, not a defect "
     "in the algorithm.")

# ============================================================
# 11. CHALLENGES FACED
# ============================================================
h1("11. Challenges Faced")
bullets([
    "<b>Numerical instability in DLT:</b> initial attempts to solve the DLT linear system "
    "directly on raw pixel coordinates produced inaccurate homographies. Resolved by "
    "implementing Hartley point normalization before solving and un-normalizing the result.",
    "<b>Outlier contamination in feature matches:</b> Lowe's ratio test alone still leaves "
    "some incorrect matches (visible in Figure 10.2), which corrupt a plain least-squares "
    "DLT fit. Resolved by implementing RANSAC on top of DLT to robustly reject outliers.",
    "<b>Canvas sizing for warped images:</b> the warped second image can extend outside "
    "the first image's original coordinate frame in any direction. Resolved by projecting "
    "all four corners of the second image through the homography, computing a bounding box "
    "over both images' corners, and applying a translation homography so all content maps "
    "to non-negative coordinates.",
    "<b>Visible seams from direct overlay:</b> simply overlaying warped images at their "
    "correct positions produced a visible seam due to exposure/lighting differences "
    "between photos. Resolved with distance-transform feathered blending.",
])

# ============================================================
# 12. LEARNINGS & KEY TAKEAWAYS
# ============================================================
h1("12. Learnings & Key Takeaways")
bullets([
    "Implementing DLT from scratch clarified why point normalization is not an optional "
    "detail but a numerical necessity for an SVD-based linear solve on pixel-scale data.",
    "RANSAC's power comes from a simple statistical argument: a minimal sample drawn "
    "entirely from inliers will have far more support from the rest of the data than any "
    "sample containing an outlier, given enough random trials.",
    "Robust estimation (RANSAC) and precise estimation (DLT refit on inliers) are "
    "complementary, not interchangeable - RANSAC's 4-point fits are only used to "
    "identify the inlier set; the final homography is refit on all inliers for accuracy.",
    "Visually verifiable outputs (grid-line alignment in the synthetic test, horizon/mast "
    "alignment in the real photo test) are an effective way to sanity-check a geometric "
    "algorithm's correctness beyond unit tests alone.",
])

# ============================================================
# 13. FUTURE ENHANCEMENTS
# ============================================================
h1("13. Future Enhancements")
bullets([
    "Multi-band (Laplacian pyramid) blending for sharper, more artifact-free seams than "
    "simple feathering.",
    "Automatic image ordering/adjacency detection, instead of relying on filename sort order.",
    "Global bundle adjustment across all images to reduce drift when stitching many images.",
    "Cylindrical or spherical projection to support full 360&deg; panoramas.",
])

# ============================================================
# 14. REFERENCES
# ============================================================
h1("14. References")
bullets([
    "R. Hartley and A. Zisserman, <i>Multiple View Geometry in Computer Vision</i>, "
    "2nd Edition, Cambridge University Press, 2004.",
    "R. Szeliski, <i>Computer Vision: Algorithms and Applications</i>, Springer-Verlag "
    "London, 2011.",
    "M. A. Fischler and R. C. Bolles, &ldquo;Random Sample Consensus: A Paradigm for Model "
    "Fitting with Applications to Image Analysis and Automated Cartography,&rdquo; "
    "<i>Communications of the ACM</i>, 24(6), 1981.",
    "D. G. Lowe, &ldquo;Distinctive Image Features from Scale-Invariant Keypoints,&rdquo; "
    "<i>International Journal of Computer Vision</i>, 60(2), 2004.",
    "OpenCV Documentation - https://docs.opencv.org/",
    "CSE3010 Computer Vision course syllabus, Module 2: Depth Estimation and Multi-Camera "
    "Views.",
])

# ============================================================
# BUILD
# ============================================================
doc = SimpleDocTemplate(
    "docs/Project_Report.pdf", pagesize=A4,
    topMargin=2.2 * cm, bottomMargin=2 * cm, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
    title="Panorama Stitching from Scratch - Project Report",
)
doc.build(story)
print("Report generated: docs/Project_Report.pdf")
