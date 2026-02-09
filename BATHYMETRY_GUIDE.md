# Bathymetric Survey Digitization Pipeline

## Overview

Production-ready Python pipeline for converting scanned hydrographic bathymetry charts into calibrated XYZ point-cloud datasets.

## Purpose

Digitizes scanned analogue hydrographic drawings containing dense numeric depth soundings into georeferenced point clouds suitable for GIS analysis, seabed modeling, and hydrographic data management.

## Key Features

- **Automated Image Processing**: Crops margins and title blocks, removes border lines
- **Advanced OCR**: Multi-mode Tesseract detection with confidence filtering
- **Interactive Calibration**: Ground control point selection with affine transformation
- **Spatial Deduplication**: Clusters and filters duplicate detections
- **Quality Control**: Comprehensive statistics and rejection tracking
- **Multiple Outputs**: XYZ, raw CSV, clean CSV, debug overlay image

## System Requirements

### Software Dependencies

**Python Packages** (install via `pip install -r requirements.txt`):
- opencv-python (image processing)
- pytesseract (OCR)
- numpy (numerical operations)
- pandas (data handling)
- pdf2image (PDF support)
- Pillow (image handling)
- matplotlib (interactive calibration)

**System Dependencies**:
- Tesseract OCR must be installed on your system
- Poppler (for PDF rendering)

### Installation

**Ubuntu/Debian** (Desktop) - Ubuntu 22.04 or newer:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils python3-tk libgl1 libglib2.0-0
pip install -r requirements.txt
```

**Ubuntu/Debian** (Desktop) - Ubuntu 20.04 or older:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils python3-tk libgl1-mesa-glx libglib2.0-0
pip install -r requirements.txt
```

**Ubuntu/Debian** (Server/Headless - any version):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
pip install -r requirements-headless.txt
```

**Automated Installation** (recommended):
```bash
# Clone the repository
git clone https://github.com/CoastCoder143/PDF-XYZ.git
cd PDF-XYZ

# Run installation script (handles all dependencies automatically)
chmod +x install.sh
./install.sh
```

**macOS**:
```bash
brew install tesseract poppler
pip install -r requirements.txt
```

**Windows**:
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases
3. Add both to PATH
4. Install Python packages: `pip install -r requirements.txt`

**Docker/Containers** - Modern Ubuntu base:
```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

**Docker/Containers** - Older Ubuntu base or headless:
```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
# Then use requirements-headless.txt
```

    && rm -rf /var/lib/apt/lists/*
```
Or use opencv-python-headless in requirements.txt

## Usage

### First Time: Interactive Calibration

```bash
python bathymetry_digitizer.py \
    --input survey_sheet.png \
    --interactive-calib \
    --outdir output/
```

**Interactive Calibration Steps**:
1. The preprocessed image will be displayed
2. Click on known control points (e.g., coordinate tick marks)
3. Enter the real-world X, Y coordinates in metres when prompted
4. Select at least 3 points (more is better)
5. Close the window when done
6. Calibration will be saved to `output/calibration.json`

### Subsequent Runs: Using Saved Calibration

```bash
python bathymetry_digitizer.py \
    --input survey_sheet.png \
    --calib-json output/calibration.json \
    --outdir results/
```

### Advanced Usage

**PDF Input with Custom Parameters**:
```bash
python bathymetry_digitizer.py \
    --input survey.pdf \
    --calib-json calibration.json \
    --outdir results/ \
    --dpi 600 \
    --min-depth 0 \
    --max-depth 50 \
    --min-conf 60 \
    --crop-params 100,200,50,50 \
    --debug
```

**Manual Cropping**:
```bash
# Crop: top=100px, bottom=200px, left=50px, right=50px
python bathymetry_digitizer.py \
    --input survey.png \
    --calib-json calibration.json \
    --outdir results/ \
    --crop-params 100,200,50,50
```

## Command-Line Arguments

### Required Arguments

- `--input PATH`: Input PNG or PDF file path
- `--outdir PATH`: Output directory for results

### Calibration (one required)

- `--interactive-calib`: Interactive calibration mode (select GCPs manually)
- `--calib-json PATH`: Load calibration from JSON file

### Optional Arguments

- `--dpi INT`: DPI for PDF rendering (default: 300)
- `--min-depth FLOAT`: Minimum valid depth in metres (default: 0.0)
- `--max-depth FLOAT`: Maximum valid depth in metres (default: 50.0)
- `--min-conf INT`: Minimum OCR confidence 0-100 (default: 50)
- `--crop-params STR`: Manual crop "top,bottom,left,right" in pixels
- `--no-auto-crop`: Disable automatic white margin detection
- `--debug`: Save intermediate preprocessing images

## Outputs

All outputs are saved to the specified `--outdir`:

1. **output.xyz**: Space-delimited XYZ point cloud
   ```
   # X (m)   Y (m)   Z (m)
   72345.678 18912.345 12.5
   72346.890 18913.456 13.2
   ```

2. **points_raw.csv**: All OCR detections (before filtering)
   - Columns: text, confidence, centroid_x, centroid_y, psm

3. **points_clean.csv**: Filtered and transformed points
   - Columns: x, y, depth, confidence, centroid_px_x, centroid_px_y

4. **debug_overlay.png**: Visual QA with bounding boxes
   - Red boxes: All OCR detections
   - Green boxes + labels: Accepted soundings

5. **calibration.json**: Affine transformation parameters (interactive mode only)

## Calibration File Format

The calibration JSON file contains:

```json
{
  "affine_matrix": [
    [a, b, c],
    [d, e, f]
  ],
  "gcps": [
    {
      "pixel": [px1, py1],
      "real": [x1, y1]
    },
    ...
  ],
  "format": "pixel_to_real",
  "units": "metres"
}
```

Transformation: `[X, Y] = affine_matrix × [px, py, 1]`

## Processing Pipeline

1. **Load Input**: Convert PDF to image (if needed) and convert to grayscale
2. **Crop Sheet**: Remove outer margins and bottom title block
3. **Preprocess**: 
   - Median blur denoising
   - Adaptive thresholding
   - Morphological operations to remove border lines
4. **OCR Detection**: 
   - Run Tesseract with multiple PSM modes (6, 11, 12)
   - Extract text, bounding boxes, confidence scores
5. **Filtering**:
   - Parse as float values
   - Apply depth range filter
   - Reject single-character noise
   - Spatial deduplication (cluster nearby detections)
6. **Calibration**: Apply affine transformation from pixel → real-world coords
7. **Export**: Write XYZ, CSVs, debug image

## Troubleshooting

### Package 'libgl1-mesa-glx' has no installation candidate

**Symptoms**: When trying to install system dependencies, you get an error like:
```
E: Package 'libgl1-mesa-glx' has no installation candidate
```

**Cause**: The package name changed in Ubuntu 22.04 and newer versions. The old package `libgl1-mesa-glx` was replaced with `libgl1`.

**Solutions**:

1. **For Ubuntu 22.04 or newer** (use modern package name):
   ```bash
   sudo apt-get update
   sudo apt-get install -y libgl1 libglib2.0-0
   ```

2. **For Ubuntu 20.04 or older** (use legacy package name):
   ```bash
   sudo apt-get update
   sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
   ```

3. **Use the automated installation script** (recommended - handles both):
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   
   The script automatically detects your system and installs the correct packages.

4. **For headless/server environments** (skip OpenGL entirely):
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr poppler-utils
   pip install -r requirements-headless.txt
   ```

### OpenCV libGL.so.1 Error (Headless Environments)

**Symptoms**: Script fails with "libGL.so.1: cannot open shared object file: No such file or directory" or similar OpenCV library errors, even after installing opencv-python via pip.

**Cause**: OpenCV requires system graphics libraries that aren't installed in headless environments (servers, Docker containers, WSL without X server, etc.).

**Solutions** (in order of recommendation):

1. **For Headless Servers/Docker** (recommended):
   ```bash
   # Uninstall regular OpenCV
   pip uninstall opencv-python opencv-contrib-python
   
   # Install headless version
   pip install opencv-python-headless
   ```
   
   The headless version works without GUI libraries and is perfect for server environments.

2. **For Desktop Linux - Ubuntu 22.04+** (if you need GUI features):
   ```bash
   sudo apt-get update
   sudo apt-get install -y libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev
   ```

3. **For Desktop Linux - Ubuntu 20.04 or older** (if you need GUI features):
   ```bash
   sudo apt-get update
   sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
   ```

4. **For CentOS/RHEL/Fedora**:
   ```bash
   sudo yum install mesa-libGL
   ```

5. **Temporary Workaround** (use environment variable):
   ```bash
   export QT_QPA_PLATFORM=offscreen
   python bathymetry_digitizer.py --input survey.pdf ...
   ```

4. **Docker/Container Environments**:
   Add to your Dockerfile:
   ```dockerfile
   RUN apt-get update && apt-get install -y \
       libgl1-mesa-glx \
       libglib2.0-0 \
       && rm -rf /var/lib/apt/lists/*
   ```
   
   Or use opencv-python-headless in requirements.txt

**Verification**:
```python
python -c "import cv2; print(cv2.__version__)"
```

If this succeeds, OpenCV is working correctly.

### Filename with Spaces Error

**Symptoms**: Script fails with "error: unrecognized arguments" when your filename contains spaces.

Example error:
```
bathymetry_digitizer.py: error: unrecognized arguments: of 15.pdf
```

**Cause**: The shell splits filenames with spaces into multiple arguments unless they are quoted.

**Solutions**:

1. **Use quotes around the filename** (recommended):
   ```bash
   python bathymetry_digitizer.py --input "98347-1 of 15.pdf" --interactive-calib --outdir output/
   ```

2. **Use double quotes**:
   ```bash
   python bathymetry_digitizer.py --input "/path/to/file with spaces.pdf" --interactive-calib --outdir output/
   ```

3. **Use single quotes** (Unix/Linux/macOS):
   ```bash
   python bathymetry_digitizer.py --input '/path/to/file with spaces.pdf' --interactive-calib --outdir output/
   ```

4. **Escape spaces with backslash** (Unix/Linux/macOS):
   ```bash
   python bathymetry_digitizer.py --input /path/to/file\ with\ spaces.pdf --interactive-calib --outdir output/
   ```

5. **Rename the file** (if possible):
   ```bash
   # Remove spaces from filename
   mv "98347-1 of 15.pdf" "98347-1_of_15.pdf"
   python bathymetry_digitizer.py --input 98347-1_of_15.pdf --interactive-calib --outdir output/
   ```

**Best Practice**: Avoid spaces in filenames for command-line tools. Use underscores (_) or hyphens (-) instead.

### Dependencies Not Installed

**Symptoms**: Script fails immediately with "ModuleNotFoundError" or "No module named 'numpy'" (or cv2, pytesseract, pandas)

**Solution**:

Install required dependencies using one of these methods:

1. **Recommended**: Install all dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

2. **Core dependencies only** (minimal installation):
   ```bash
   pip install numpy opencv-python pytesseract pandas
   ```

3. **System dependencies** (must be installed before Python packages):
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr poppler-utils python3-tk`
   - **macOS**: `brew install tesseract poppler`
   - **Windows**: Install Tesseract from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

After installation, verify Tesseract is accessible:
```bash
tesseract --version
```

### No OCR Detections

**Symptoms**: "No OCR detections found"

**Solutions**:
- Increase DPI: `--dpi 600` or `--dpi 1200`
- Reduce minimum confidence: `--min-conf 30`
- Check that Tesseract is installed: `tesseract --version`
- Enable debug mode to inspect preprocessing: `--debug`

### Wrong Detections

**Symptoms**: Border text or title block detected as soundings

**Solutions**:
- Adjust crop parameters: `--crop-params 100,300,100,100`
- Tighten depth range: `--min-depth 5 --max-depth 30`
- Increase minimum confidence: `--min-conf 70`

### Duplicate Points

**Symptoms**: Same sounding detected multiple times

**Solutions**:
- Adjust `DEDUP_RADIUS_PX` in code (default: 10 pixels)
- Lower values = less aggressive deduplication
- Higher values = more aggressive deduplication

### Coordinate Errors

**Symptoms**: XY coordinates don't match expected values

**Solutions**:
- Verify calibration GCPs are correct
- Use more GCPs (5-10 recommended)
- Ensure GCPs are well-distributed across the image
- Check affine transformation RMS error in logs
- Re-run interactive calibration if necessary

### Low Accuracy

**Symptoms**: OCR misreads numbers (e.g., 13 vs 15)

**Solutions**:
- Increase input resolution: `--dpi 600` or higher
- Inspect preprocessed images with `--debug`
- Adjust preprocessing parameters in code if needed
- Consider manual verification of critical areas

## Parameter Tuning Guide

### DPI Selection
- **300 DPI**: Fast, good for clear scans
- **600 DPI**: Better quality, recommended for typical use
- **1200 DPI**: Highest quality, very slow, for poor quality scans

### Depth Range
- Set based on survey area characteristics
- Too wide: More false positives from title block text
- Too narrow: May exclude valid soundings

### Confidence Threshold
- **30-40**: Very permissive, many false positives
- **50-60**: Balanced (recommended)
- **70-80**: Very strict, may miss valid detections

### Crop Parameters
- Measure in image viewer (pixels from edges)
- Format: `top,bottom,left,right`
- Bottom should exclude entire title block (typically 10-20% of height)
- Test with `--debug` to verify crop region

## Quality Control

After each run, review the summary output:

```
==============================================================
QUALITY CONTROL SUMMARY
==============================================================
Total OCR detections:     1247
Rejected (parse error):   52
Rejected (out of range):  183
Rejected (too short):     8
Rejected (duplicate):     124
ACCEPTED SOUNDINGS:       880
==============================================================

Depth statistics:
  Min: 8.50 m
  Max: 24.30 m
  Mean: 15.67 m
  Std: 3.42 m
==============================================================
```

**What to check**:
- Accepted count should be reasonable for survey density
- High parse errors → OCR quality issue
- High range rejections → adjust depth range
- High duplicates → normal, indicates good spatial coverage

## Best Practices

1. **Always use interactive calibration first** for a new survey area
2. **Select well-distributed GCPs** across the entire map extent
3. **Use coordinate tick marks or corners** as GCPs when possible
4. **Verify outputs** using the debug overlay image
5. **Compare statistics** with expected survey characteristics
6. **Reuse calibration** for surveys from the same area/scale

## Limitations

- Requires numeric soundings as text (not contour lines or raster shading)
- Assumes reasonably horizontal text orientation
- Best for surveys at 1:500 to 1:5000 scale
- OCR accuracy depends on scan quality
- Manual verification recommended for critical applications

## Integration with GIS

Import the XYZ file into GIS software:

**QGIS**:
```
Layer → Add Layer → Add Delimited Text Layer
- File: output.xyz
- File format: Custom delimiters (Space)
- X field: field_1
- Y field: field_2
- Z field: field_3
```

**ArcGIS**:
```
ASCII 3D to Feature Class tool
- Input: output.xyz
- Input coordinate format: XYZ
```

## Support

For issues or questions:
1. Check the debug overlay image
2. Review the QC summary statistics
3. Enable `--debug` mode to inspect preprocessing
4. Consult the troubleshooting section above

## License

MIT License - See LICENSE file
