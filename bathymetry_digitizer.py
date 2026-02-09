#!/usr/bin/env python3
"""
BATHYMETRIC SURVEY DIGITIZATION PIPELINE
=========================================

PURPOSE
-------
Converts scanned hydrographic bathymetry charts (PNG or PDF) containing dense
spot soundings into calibrated XYZ point-cloud datasets.

DEPENDENCIES
------------
Required:
    - opencv-python (cv2)
    - pytesseract
    - numpy
    - pandas
    
Optional:
    - pdf2image (for PDF input)
    - Pillow
    - matplotlib (for interactive calibration)

System:
    - Tesseract OCR must be installed on the system

CALIBRATION
-----------
The pipeline converts pixel coordinates to real-world XY coordinates using an
affine transformation. Two modes are supported:

1. Interactive Mode:
   - Display the preprocessed image
   - User clicks ≥3 ground control points (GCPs)
   - User inputs known (X, Y) coordinates in metres
   - Solve affine transform via least squares
   - Save calibration to JSON

2. Non-Interactive Mode:
   - Load pre-computed calibration from JSON file
   
Affine transform: [X, Y] = A * [px, py, 1]
Where A is a 2x3 matrix computed from GCPs.

HOW TO RUN
----------
Interactive calibration (first time):
    python bathymetry_digitizer.py --input survey.png --interactive-calib --outdir output/

Using saved calibration:
    python bathymetry_digitizer.py --input survey.png --calib-json calibration.json --outdir output/

With custom parameters:
    python bathymetry_digitizer.py --input survey.pdf \\
        --calib-json calibration.json \\
        --outdir results/ \\
        --min-depth 0 \\
        --max-depth 50 \\
        --min-conf 50 \\
        --crop-params 50,100,50,200

ASSUMPTIONS
-----------
1. Input image contains numeric depth soundings as small text
2. Depths are within a reasonable range (default 0-50m)
3. Title block is at the bottom of the sheet
4. Border/frame can be removed via cropping
5. OCR text consists primarily of digits, decimal points, and minus signs

FAILURE MODES & TUNING
----------------------
- Low OCR accuracy: Increase DPI (--dpi), adjust preprocessing
- Wrong detections: Tighten depth range (--min-depth, --max-depth)
- Duplicate points: Adjust dedup radius (modify DEDUP_RADIUS_PX in code)
- Missing soundings: Try different PSM modes, reduce --min-conf
- Coordinate errors: Verify calibration GCPs, check affine residuals

AUTHOR
------
Agentic Python Automation Engineer
Production-ready bathymetric survey digitization system
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import warnings

# Core required imports with helpful error message
try:
    import numpy as np
except ImportError as e:
    print("\n" + "="*70)
    print("ERROR: Required dependencies not installed")
    print("="*70)
    print(f"\nMissing module: {e}")
    print("\nPlease install required dependencies:")
    print("  pip install -r requirements.txt")
    print("\nOr install core dependencies:")
    print("  pip install numpy opencv-python pytesseract pandas")
    print("\nSee BATHYMETRY_GUIDE.md for detailed installation instructions.")
    print("="*70 + "\n")
    sys.exit(1)

try:
    import cv2
except ImportError as e:
    # Check if this is a libGL.so error (common in headless environments)
    error_msg = str(e)
    if 'libGL.so' in error_msg or 'libgthread' in error_msg or 'libSM.so' in error_msg:
        print("\n" + "="*70)
        print("ERROR: OpenCV system library not found")
        print("="*70)
        print(f"\nError details: {e}")
        print("\nThis error occurs when system graphics libraries are missing.")
        print("This is common in headless servers or Docker containers.")
        print("\nSOLUTION OPTIONS:")
        print("\n1. Install system graphics libraries (recommended for desktop):")
        print("   Ubuntu/Debian:")
        print("     sudo apt-get update")
        print("     sudo apt-get install -y libgl1-mesa-glx libglib2.0-0")
        print("\n   CentOS/RHEL:")
        print("     sudo yum install mesa-libGL")
        print("\n2. Use headless OpenCV (recommended for servers):")
        print("   pip uninstall opencv-python")
        print("   pip install opencv-python-headless")
        print("\n3. Set environment variable (temporary workaround):")
        print("   export QT_QPA_PLATFORM=offscreen")
        print("\nSee BATHYMETRY_GUIDE.md for detailed troubleshooting.")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("ERROR: OpenCV (cv2) not installed")
        print("="*70)
        print(f"\nMissing module: {e}")
        print("\nPlease install OpenCV:")
        print("  pip install opencv-python")
        print("\nOr install all dependencies:")
        print("  pip install -r requirements.txt")
        print("="*70 + "\n")
    sys.exit(1)

try:
    import pytesseract
    import pandas as pd
except ImportError as e:
    print("\n" + "="*70)
    print("ERROR: Required dependencies not installed")
    print("="*70)
    print(f"\nMissing module: {e}")
    print("\nPlease install required dependencies:")
    print("  pip install -r requirements.txt")
    print("\nOr install missing dependency:")
    print("  pip install pytesseract pandas")
    print("\nSee BATHYMETRY_GUIDE.md for detailed installation instructions.")
    print("="*70 + "\n")
    sys.exit(1)

# Optional imports
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# OCR Configuration
TESSERACT_WHITELIST = '0123456789.-,'
PSM_MODES = [6, 11, 12]  # Page segmentation modes to try
DEFAULT_MIN_CONFIDENCE = 50

# Filtering
DEFAULT_MIN_DEPTH = 0.0
DEFAULT_MAX_DEPTH = 50.0
MIN_TOKEN_LENGTH = 2  # Minimum characters for valid depth (reject single digits)
DEDUP_RADIUS_PX = 10  # Pixel radius for duplicate clustering

# Preprocessing
DENOISE_KERNEL = 5
ADAPTIVE_BLOCK_SIZE = 11
ADAPTIVE_C = 2
MORPH_KERNEL_SIZE = (3, 20)  # For removing horizontal/vertical lines

# Output files
OUTPUT_XYZ = "output.xyz"
OUTPUT_RAW_CSV = "points_raw.csv"
OUTPUT_CLEAN_CSV = "points_clean.csv"
OUTPUT_DEBUG_IMAGE = "debug_overlay.png"
CALIBRATION_FILE = "calibration.json"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)


def parse_crop_params(crop_str: Optional[str]) -> Optional[Tuple[int, int, int, int]]:
    """
    Parse crop parameters from string
    
    Args:
        crop_str: String in format "top,bottom,left,right"
        
    Returns:
        Tuple of (top, bottom, left, right) or None
    """
    if not crop_str:
        return None
    try:
        parts = [int(x.strip()) for x in crop_str.split(',')]
        if len(parts) != 4:
            raise ValueError
        return tuple(parts)
    except (ValueError, AttributeError):
        logger.warning(f"Invalid crop parameters: {crop_str}")
        return None


# ============================================================================
# CORE PIPELINE FUNCTIONS
# ============================================================================

def load_input(input_path: str, dpi: int = 300) -> np.ndarray:
    """
    Load input image from PNG or PDF
    
    Args:
        input_path: Path to input file
        dpi: DPI for PDF rendering (default 300)
        
    Returns:
        Grayscale image as numpy array
    """
    logger.info(f"Loading input: {input_path}")
    
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Handle PDF
    if path.suffix.lower() == '.pdf':
        if not PDF_SUPPORT:
            raise ImportError("pdf2image not installed. Install with: pip install pdf2image")
        
        logger.info(f"Converting PDF to image at {dpi} DPI...")
        images = convert_from_path(input_path, dpi=dpi)
        if not images:
            raise ValueError("Failed to convert PDF")
        
        # Use first page
        image = np.array(images[0])
    else:
        # Handle image formats
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Failed to load image: {input_path}")
    
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    logger.info(f"Loaded image: {gray.shape[1]}x{gray.shape[0]} pixels")
    return gray


def crop_sheet(image: np.ndarray, 
               crop_params: Optional[Tuple[int, int, int, int]] = None,
               auto_crop: bool = True) -> Tuple[np.ndarray, Dict[str, int]]:
    """
    Crop outer margins and bottom title block
    
    Args:
        image: Input grayscale image
        crop_params: Manual crop as (top, bottom, left, right) pixels to remove
        auto_crop: Attempt automatic white margin detection
        
    Returns:
        Cropped image and crop info dict
    """
    logger.info("Cropping sheet...")
    
    h, w = image.shape
    
    if crop_params:
        top, bottom, left, right = crop_params
        logger.info(f"Using manual crop: top={top}, bottom={bottom}, left={left}, right={right}")
    elif auto_crop:
        # Simple auto-crop: remove very white edges
        # Threshold to detect white regions
        _, binary = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY)
        
        # Find content boundaries
        rows_sum = np.sum(binary < 255, axis=1)
        cols_sum = np.sum(binary < 255, axis=0)
        
        # Find first/last rows and cols with content
        content_rows = np.where(rows_sum > w * 0.01)[0]  # At least 1% of width has content
        content_cols = np.where(cols_sum > h * 0.01)[0]  # At least 1% of height has content
        
        if len(content_rows) > 0 and len(content_cols) > 0:
            top = max(0, content_rows[0] - 10)
            bottom = max(0, h - content_rows[-1] - 10)
            left = max(0, content_cols[0] - 10)
            right = max(0, w - content_cols[-1] - 10)
            
            # Reserve extra space at bottom for title block
            bottom = max(bottom, int(h * 0.15))  # Remove at least 15% from bottom
            
            logger.info(f"Auto-detected crop: top={top}, bottom={bottom}, left={left}, right={right}")
        else:
            # Fallback to defaults
            top, bottom, left, right = 50, int(h * 0.15), 50, 50
            logger.warning("Auto-crop failed, using defaults")
    else:
        # Default crop
        top, bottom, left, right = 50, int(h * 0.15), 50, 50
        logger.info(f"Using default crop")
    
    # Apply crop
    cropped = image[top:h-bottom, left:w-right]
    
    crop_info = {
        'top': top,
        'bottom': bottom,
        'left': left,
        'right': right,
        'original_height': h,
        'original_width': w
    }
    
    logger.info(f"Cropped to: {cropped.shape[1]}x{cropped.shape[0]} pixels")
    return cropped, crop_info


def preprocess_image(image: np.ndarray, debug_dir: Optional[str] = None) -> np.ndarray:
    """
    Preprocess image for optimal OCR
    
    Args:
        image: Input grayscale image
        debug_dir: Optional directory to save intermediate images
        
    Returns:
        Preprocessed image
    """
    logger.info("Preprocessing image...")
    
    # 1. Denoise
    denoised = cv2.medianBlur(image, DENOISE_KERNEL)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "01_denoised.png"), denoised)
    
    # 2. Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        ADAPTIVE_BLOCK_SIZE,
        ADAPTIVE_C
    )
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "02_threshold.png"), thresh)
    
    # 3. Morphological operations to remove long straight lines (borders)
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, MORPH_KERNEL_SIZE)
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    
    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (MORPH_KERNEL_SIZE[1], MORPH_KERNEL_SIZE[0]))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
    
    # Combine detected lines
    lines = cv2.bitwise_or(detect_horizontal, detect_vertical)
    
    # Remove lines from original
    processed = cv2.bitwise_and(thresh, cv2.bitwise_not(lines))
    
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "03_lines_removed.png"), processed)
    
    logger.info("Preprocessing complete")
    return processed


def ocr_soundings(image: np.ndarray, 
                  min_conf: int = DEFAULT_MIN_CONFIDENCE) -> List[Dict[str, Any]]:
    """
    Extract numeric soundings using Tesseract OCR with bounding boxes
    
    Args:
        image: Preprocessed grayscale image
        min_conf: Minimum confidence threshold (0-100)
        
    Returns:
        List of detection dicts with keys: text, bbox, conf, centroid
    """
    logger.info("Running OCR detection...")
    
    detections = []
    
    # Try multiple PSM modes
    for psm in PSM_MODES:
        config = f'--psm {psm} -c tessedit_char_whitelist={TESSERACT_WHITELIST}'
        
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])
                
                # Skip low confidence and empty text
                if conf < min_conf or not text:
                    continue
                
                # Get bounding box
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                # Compute centroid
                cx = x + w / 2
                cy = y + h / 2
                
                detections.append({
                    'text': text,
                    'bbox': (x, y, w, h),
                    'conf': conf,
                    'centroid': (cx, cy),
                    'psm': psm
                })
                
        except Exception as e:
            logger.warning(f"OCR failed for PSM {psm}: {e}")
            continue
    
    logger.info(f"OCR detected {len(detections)} candidates")
    return detections


def filter_soundings(detections: List[Dict[str, Any]],
                    min_depth: float = DEFAULT_MIN_DEPTH,
                    max_depth: float = DEFAULT_MAX_DEPTH) -> Tuple[List[Dict], Dict]:
    """
    Filter and deduplicate OCR detections
    
    Args:
        detections: List of OCR detection dicts
        min_depth: Minimum valid depth
        max_depth: Maximum valid depth
        
    Returns:
        Filtered detections and rejection stats
    """
    logger.info("Filtering soundings...")
    
    stats = {
        'total': len(detections),
        'rejected_parse': 0,
        'rejected_range': 0,
        'rejected_short': 0,
        'rejected_duplicate': 0,
        'accepted': 0
    }
    
    # Parse and filter
    valid_detections = []
    
    for det in detections:
        text = det['text']
        
        # Reject single characters
        if len(text) < MIN_TOKEN_LENGTH:
            stats['rejected_short'] += 1
            continue
        
        # Try to parse as float
        try:
            # Clean text: remove commas
            cleaned = text.replace(',', '')
            depth = float(cleaned)
        except ValueError:
            stats['rejected_parse'] += 1
            continue
        
        # Check range
        if not (min_depth <= depth <= max_depth):
            stats['rejected_range'] += 1
            continue
        
        # Store parsed depth
        det['depth'] = depth
        valid_detections.append(det)
    
    # Deduplicate by spatial clustering
    if len(valid_detections) == 0:
        logger.warning("No valid detections after filtering")
        return [], stats
    
    # Sort by confidence (descending)
    valid_detections.sort(key=lambda x: x['conf'], reverse=True)
    
    # Cluster nearby detections
    accepted = []
    rejected_indices = set()
    
    for i, det in enumerate(valid_detections):
        if i in rejected_indices:
            continue
        
        cx1, cy1 = det['centroid']
        accepted.append(det)
        
        # Mark nearby detections as duplicates
        for j in range(i + 1, len(valid_detections)):
            if j in rejected_indices:
                continue
            
            cx2, cy2 = valid_detections[j]['centroid']
            dist = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
            
            if dist < DEDUP_RADIUS_PX:
                rejected_indices.add(j)
                stats['rejected_duplicate'] += 1
    
    stats['accepted'] = len(accepted)
    
    logger.info(f"Accepted {stats['accepted']} soundings after filtering")
    logger.info(f"Rejected: parse={stats['rejected_parse']}, "
                f"range={stats['rejected_range']}, "
                f"short={stats['rejected_short']}, "
                f"duplicate={stats['rejected_duplicate']}")
    
    return accepted, stats


def calibrate_affine_interactive(image: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
    """
    Interactive calibration using matplotlib
    
    Args:
        image: Reference image for GCP selection
        
    Returns:
        Affine transformation matrix (2x3) and list of GCPs
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib not available for interactive calibration")
    
    # Set backend for interactive mode
    import matplotlib
    matplotlib.use('TkAgg')
    
    logger.info("Starting interactive calibration...")
    logger.info("Click on ground control points in the image")
    logger.info("Close the window when done (need at least 3 points)")
    
    gcps = []
    
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.imshow(image, cmap='gray')
    ax.set_title("Click on Ground Control Points (Close window when done)")
    
    def onclick(event):
        if event.inaxes != ax:
            return
        
        px, py = event.xdata, event.ydata
        
        # Prompt for real-world coordinates
        print(f"\nPoint {len(gcps) + 1}: clicked at pixel ({px:.1f}, {py:.1f})")
        
        try:
            x_str = input("  Enter X coordinate (metres): ")
            y_str = input("  Enter Y coordinate (metres): ")
            
            x_real = float(x_str)
            y_real = float(y_str)
            
            gcps.append({
                'pixel': (px, py),
                'real': (x_real, y_real)
            })
            
            # Draw marker
            ax.plot(px, py, 'ro', markersize=10)
            ax.text(px + 20, py + 20, f"GCP {len(gcps)}", 
                   color='red', fontsize=12, fontweight='bold')
            plt.draw()
            
            print(f"  Added GCP {len(gcps)}: pixel=({px:.1f}, {py:.1f}), real=({x_real}, {y_real})")
            
        except (ValueError, EOFError, KeyboardInterrupt):
            print("  Skipped point")
    
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    
    if len(gcps) < 3:
        raise ValueError(f"Need at least 3 GCPs, got {len(gcps)}")
    
    # Compute affine transform
    logger.info(f"Computing affine transform from {len(gcps)} GCPs...")
    
    # Build matrices for least squares
    # [X]   [a b c]   [px]
    # [Y] = [d e f] * [py]
    #                 [1 ]
    
    px_coords = np.array([[gcp['pixel'][0], gcp['pixel'][1], 1.0] for gcp in gcps])
    real_coords = np.array([[gcp['real'][0], gcp['real'][1]] for gcp in gcps])
    
    # Solve for affine matrix
    affine_matrix, residuals, rank, s = np.linalg.lstsq(px_coords, real_coords, rcond=None)
    affine_matrix = affine_matrix.T  # Shape (2, 3)
    
    # Compute residuals
    predicted = px_coords @ affine_matrix.T
    errors = real_coords - predicted
    rms_error = np.sqrt(np.mean(errors**2))
    
    logger.info(f"Affine calibration complete")
    logger.info(f"RMS error: {rms_error:.4f} metres")
    
    return affine_matrix, gcps


def calibrate_affine_from_json(calib_path: str) -> np.ndarray:
    """
    Load affine calibration from JSON file
    
    Args:
        calib_path: Path to calibration JSON
        
    Returns:
        Affine transformation matrix (2x3)
    """
    logger.info(f"Loading calibration from: {calib_path}")
    
    with open(calib_path, 'r') as f:
        calib_data = json.load(f)
    
    if 'affine_matrix' not in calib_data:
        raise ValueError("Invalid calibration file: missing 'affine_matrix'")
    
    affine_matrix = np.array(calib_data['affine_matrix'])
    
    if affine_matrix.shape != (2, 3):
        raise ValueError(f"Invalid affine matrix shape: {affine_matrix.shape}")
    
    logger.info("Calibration loaded successfully")
    return affine_matrix


def save_calibration(affine_matrix: np.ndarray, 
                    gcps: List[Dict], 
                    output_path: str) -> None:
    """
    Save calibration to JSON
    
    Args:
        affine_matrix: 2x3 affine transformation matrix
        gcps: List of ground control points
        output_path: Output JSON path
    """
    calib_data = {
        'affine_matrix': affine_matrix.tolist(),
        'gcps': gcps,
        'format': 'pixel_to_real',
        'units': 'metres'
    }
    
    with open(output_path, 'w') as f:
        json.dump(calib_data, f, indent=2)
    
    logger.info(f"Calibration saved to: {output_path}")


def apply_transform(detections: List[Dict], 
                   affine_matrix: np.ndarray,
                   crop_info: Dict) -> List[Dict]:
    """
    Apply affine transformation to convert pixel centroids to real-world XY
    
    Args:
        detections: List of detection dicts with centroids
        affine_matrix: 2x3 affine transformation matrix
        crop_info: Crop offset information
        
    Returns:
        Detections with added 'x' and 'y' fields in metres
    """
    logger.info("Applying coordinate transformation...")
    
    for det in detections:
        # Get centroid in cropped image space
        cx_crop, cy_crop = det['centroid']
        
        # Convert to original image space
        cx_orig = cx_crop + crop_info['left']
        cy_orig = cy_crop + crop_info['top']
        
        # Apply affine transform: [X, Y] = A * [px, py, 1]
        pixel_coords = np.array([cx_orig, cy_orig, 1.0])
        real_coords = affine_matrix @ pixel_coords
        
        det['x'] = real_coords[0]
        det['y'] = real_coords[1]
    
    logger.info(f"Transformed {len(detections)} points to real-world coordinates")
    return detections


def export_outputs(detections: List[Dict],
                  raw_detections: List[Dict],
                  image: np.ndarray,
                  output_dir: str,
                  stats: Dict) -> None:
    """
    Export XYZ file, CSV files, and debug overlay image
    
    Args:
        detections: Filtered and transformed detections
        raw_detections: All raw OCR detections
        image: Reference image for debug overlay
        output_dir: Output directory
        stats: Filtering statistics
    """
    logger.info("Exporting outputs...")
    
    ensure_dir(output_dir)
    
    # 1. Export XYZ file
    xyz_path = os.path.join(output_dir, OUTPUT_XYZ)
    with open(xyz_path, 'w') as f:
        f.write("# X (m)   Y (m)   Z (m)\n")
        for det in detections:
            f.write(f"{det['x']:.6f} {det['y']:.6f} {det['depth']:.6f}\n")
    logger.info(f"Wrote XYZ file: {xyz_path} ({len(detections)} points)")
    
    # 2. Export raw CSV
    raw_csv_path = os.path.join(output_dir, OUTPUT_RAW_CSV)
    raw_df = pd.DataFrame([{
        'text': det['text'],
        'confidence': det['conf'],
        'centroid_x': det['centroid'][0],
        'centroid_y': det['centroid'][1],
        'psm': det['psm']
    } for det in raw_detections])
    raw_df.to_csv(raw_csv_path, index=False)
    logger.info(f"Wrote raw CSV: {raw_csv_path}")
    
    # 3. Export clean CSV
    clean_csv_path = os.path.join(output_dir, OUTPUT_CLEAN_CSV)
    clean_df = pd.DataFrame([{
        'x': det['x'],
        'y': det['y'],
        'depth': det['depth'],
        'confidence': det['conf'],
        'centroid_px_x': det['centroid'][0],
        'centroid_px_y': det['centroid'][1]
    } for det in detections])
    clean_df.to_csv(clean_csv_path, index=False)
    logger.info(f"Wrote clean CSV: {clean_csv_path}")
    
    # 4. Export debug overlay image
    debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # Draw all detections in red
    for det in raw_detections:
        x, y, w, h = det['bbox']
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 0, 255), 1)
    
    # Draw accepted detections in green with labels
    for det in detections:
        x, y, w, h = det['bbox']
        cx, cy = det['centroid']
        
        # Green box
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Label with depth
        label = f"{det['depth']:.1f}"
        cv2.putText(debug_image, label, (int(cx)+5, int(cy)-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    debug_path = os.path.join(output_dir, OUTPUT_DEBUG_IMAGE)
    cv2.imwrite(debug_path, debug_image)
    logger.info(f"Wrote debug image: {debug_path}")
    
    # 5. Print summary
    print("\n" + "="*60)
    print("QUALITY CONTROL SUMMARY")
    print("="*60)
    print(f"Total OCR detections:     {stats['total']}")
    print(f"Rejected (parse error):   {stats['rejected_parse']}")
    print(f"Rejected (out of range):  {stats['rejected_range']}")
    print(f"Rejected (too short):     {stats['rejected_short']}")
    print(f"Rejected (duplicate):     {stats['rejected_duplicate']}")
    print(f"ACCEPTED SOUNDINGS:       {stats['accepted']}")
    print("="*60)
    
    if len(detections) > 0:
        print(f"\nDepth statistics:")
        depths = [det['depth'] for det in detections]
        print(f"  Min: {min(depths):.2f} m")
        print(f"  Max: {max(depths):.2f} m")
        print(f"  Mean: {np.mean(depths):.2f} m")
        print(f"  Std: {np.std(depths):.2f} m")
    
    print(f"\nOutputs written to: {output_dir}")
    print("="*60 + "\n")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(
        description='Bathymetric Survey Digitization Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive calibration:
    %(prog)s --input survey.png --interactive-calib --outdir output/
    
  Using saved calibration:
    %(prog)s --input survey.png --calib-json calibration.json --outdir output/
    
  With filename containing spaces (use quotes):
    %(prog)s --input "survey 1 of 5.pdf" --interactive-calib --outdir output/
    
  With custom parameters:
    %(prog)s --input survey.pdf --calib-json cal.json --outdir results/ \\
             --min-depth 5 --max-depth 30 --min-conf 60 \\
             --crop-params 100,200,50,50

Note: If your filename contains spaces, enclose it in quotes:
  --input "file with spaces.pdf"
        """
    )
    
    # Required arguments
    parser.add_argument('--input', required=True,
                       help='Input PNG or PDF file (use quotes if filename has spaces)')
    parser.add_argument('--outdir', required=True,
                       help='Output directory')
    
    # Calibration arguments
    calib_group = parser.add_mutually_exclusive_group(required=True)
    calib_group.add_argument('--interactive-calib', action='store_true',
                            help='Interactive calibration mode')
    calib_group.add_argument('--calib-json',
                            help='Path to calibration JSON file')
    
    # Optional arguments
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI for PDF rendering (default: 300)')
    parser.add_argument('--min-depth', type=float, default=DEFAULT_MIN_DEPTH,
                       help=f'Minimum valid depth (default: {DEFAULT_MIN_DEPTH})')
    parser.add_argument('--max-depth', type=float, default=DEFAULT_MAX_DEPTH,
                       help=f'Maximum valid depth (default: {DEFAULT_MAX_DEPTH})')
    parser.add_argument('--min-conf', type=int, default=DEFAULT_MIN_CONFIDENCE,
                       help=f'Minimum OCR confidence (default: {DEFAULT_MIN_CONFIDENCE})')
    parser.add_argument('--crop-params',
                       help='Manual crop: "top,bottom,left,right" in pixels')
    parser.add_argument('--no-auto-crop', action='store_true',
                       help='Disable automatic cropping')
    parser.add_argument('--debug', action='store_true',
                       help='Save intermediate debug images')
    
    # Custom error handling for common mistakes
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # Check if this might be a filename with spaces issue
        if e.code != 0 and len(sys.argv) > 1:
            # Look for cases where --input or --calib-json is followed by multiple unquoted args
            input_idx = None
            try:
                input_idx = sys.argv.index('--input')
            except ValueError:
                pass
            
            calib_idx = None
            try:
                calib_idx = sys.argv.index('--calib-json')
            except ValueError:
                pass
            
            # Check if there are multiple non-flag arguments after --input or --calib-json
            for idx in [input_idx, calib_idx]:
                if idx is not None and idx < len(sys.argv) - 1:
                    # Collect all non-flag arguments after this flag
                    parts = []
                    for i in range(idx + 1, len(sys.argv)):
                        if sys.argv[i].startswith('-'):
                            break
                        parts.append(sys.argv[i])
                    
                    # If we have multiple parts, likely a filename with spaces
                    if len(parts) > 1:
                        flag = sys.argv[idx]
                        suggested_filename = ' '.join(parts)
                        print("\n" + "="*70)
                        print("ERROR: Filename with spaces must be quoted!")
                        print("="*70)
                        print("\nYour command has an unquoted filename with spaces.")
                        print(f"\nDetected filename: {suggested_filename}")
                        print(f"\nCorrect usage:")
                        print(f'  {flag} "{suggested_filename}"')
                        print("\nFull example:")
                        print(f'  python bathymetry_digitizer.py {flag} "{suggested_filename}" --interactive-calib --outdir output/')
                        print("\nAlternatively, rename the file without spaces:")
                        print(f'  mv "{suggested_filename}" "{suggested_filename.replace(" ", "_")}"')
                        print("\n" + "="*70 + "\n")
                        sys.exit(1)
        raise
    
    # Validate arguments
    if args.interactive_calib and not MATPLOTLIB_AVAILABLE:
        logger.error("Interactive calibration requires matplotlib")
        sys.exit(1)
    
    # Setup
    ensure_dir(args.outdir)
    debug_dir = os.path.join(args.outdir, 'debug') if args.debug else None
    if debug_dir:
        ensure_dir(debug_dir)
    
    try:
        # A. Load input
        image = load_input(args.input, dpi=args.dpi)
        
        # B. Crop sheet
        crop_params = parse_crop_params(args.crop_params)
        cropped, crop_info = crop_sheet(
            image,
            crop_params=crop_params,
            auto_crop=not args.no_auto_crop
        )
        
        if debug_dir:
            cv2.imwrite(os.path.join(debug_dir, "00_cropped.png"), cropped)
        
        # C. Preprocess
        preprocessed = preprocess_image(cropped, debug_dir=debug_dir)
        
        # D. OCR detection
        raw_detections = ocr_soundings(preprocessed, min_conf=args.min_conf)
        
        if len(raw_detections) == 0:
            logger.error("No OCR detections found. Try adjusting parameters.")
            sys.exit(1)
        
        # E. Parse and filter
        filtered_detections, stats = filter_soundings(
            raw_detections,
            min_depth=args.min_depth,
            max_depth=args.max_depth
        )
        
        if len(filtered_detections) == 0:
            logger.error("No valid soundings after filtering. Try adjusting depth range.")
            sys.exit(1)
        
        # F. Calibration
        if args.interactive_calib:
            affine_matrix, gcps = calibrate_affine_interactive(preprocessed)
            
            # Save calibration
            calib_path = os.path.join(args.outdir, CALIBRATION_FILE)
            save_calibration(affine_matrix, gcps, calib_path)
        else:
            affine_matrix = calibrate_affine_from_json(args.calib_json)
        
        # G. Transform coordinates
        transformed_detections = apply_transform(
            filtered_detections,
            affine_matrix,
            crop_info
        )
        
        # H. Export outputs
        export_outputs(
            transformed_detections,
            raw_detections,
            preprocessed,
            args.outdir,
            stats
        )
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
