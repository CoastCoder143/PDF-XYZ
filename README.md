# PDF-XYZ

Advanced tools for digitizing bathymetric survey data from scanned documents.

## Tools Included

This repository contains two complementary tools for processing bathymetric data:

### 1. Bathymetric Survey Digitizer (`bathymetry_digitizer.py`) ⭐ **Production-Ready**

**Purpose**: Production-ready pipeline for digitizing scanned hydrographic charts with dense spot soundings into calibrated XYZ point clouds.

**Key Features**:
- **Interactive Calibration**: Ground control point selection with affine transformation
- **Automated Processing**: Crops margins/title blocks, removes border lines  
- **Advanced OCR**: Multi-mode Tesseract with confidence filtering
- **Spatial Deduplication**: Clusters and filters duplicate detections
- **Multiple Outputs**: XYZ, raw CSV, clean CSV, debug overlay
- **Quality Control**: Comprehensive statistics and validation

**Best For**: Professional hydrographic survey digitization, bathymetric mapping projects, GIS integration

📖 **[Complete Guide →](BATHYMETRY_GUIDE.md)**

**Quick Start**:
```bash
# Interactive calibration (first time)
python bathymetry_digitizer.py --input survey.png --interactive-calib --outdir output/

# Using saved calibration
python bathymetry_digitizer.py --input survey.png --calib-json calibration.json --outdir results/
```

### 2. Simple PDF to XYZ Converter (`pdf_to_xyz.py`)

**Purpose**: Basic converter for PDFs containing coordinate data in text format.

**Key Features**:
- **Multiple OCR Engines**: Tesseract, EasyOCR, and PaddleOCR
- **Advanced Preprocessing**: Denoising, deskewing, thresholding
- **Flexible Format Support**: Various coordinate notations
- **High DPI Support**: Configurable resolution

**Best For**: Quick conversions of PDFs with pre-formatted XYZ coordinates

📖 **[Quick Start Guide →](QUICKSTART.md)**

**Quick Start**:
```bash
python pdf_to_xyz.py input.pdf
```

---

## Installation

### Quick Start (Automated)

**Easiest way** - Use the installation script:
```bash
# Clone the repository
git clone https://github.com/CoastCoder143/PDF-XYZ.git
cd PDF-XYZ

# Run automated installation
chmod +x install.sh
./install.sh
```

The script automatically:
- Detects your operating system
- Installs system dependencies
- Creates a Python virtual environment
- Installs all Python packages
- Verifies the installation

### Manual Installation

### Prerequisites

1. **System Dependencies** (for Tesseract OCR):
   ```bash
   # Ubuntu/Debian 22.04+ (Desktop)
   sudo apt-get update
   sudo apt-get install tesseract-ocr poppler-utils libgl1
   
   # Ubuntu/Debian 20.04 or older (Desktop)
   sudo apt-get update
   sudo apt-get install tesseract-ocr poppler-utils libgl1-mesa-glx
   
   # Ubuntu/Debian (Server/Headless - any version)
   sudo apt-get update
   sudo apt-get install tesseract-ocr poppler-utils
   # Note: Use requirements-headless.txt for servers
   
   # macOS
   brew install tesseract poppler
   
   # Windows
   # Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   # Download and install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
   ```

2. **Python Dependencies**:
   ```bash
   # For desktop/workstation
   pip install -r requirements.txt
   
   # For servers/headless environments (if you get libGL.so.1 errors)
   pip install -r requirements-headless.txt
   ```

**Troubleshooting**: 
- If you get "Package 'libgl1-mesa-glx' has no installation candidate", you're on Ubuntu 22.04+ - use `libgl1` instead
- If you encounter "libGL.so.1" errors, see [BATHYMETRY_GUIDE.md](BATHYMETRY_GUIDE.md#opencv-libglso1-error-headless-environments) for solutions

## Choosing the Right Tool

| Use Case | Recommended Tool |
|----------|-----------------|
| Professional hydrographic survey digitization | `bathymetry_digitizer.py` |
| Scanned charts with spot soundings | `bathymetry_digitizer.py` |
| Need georeferenced coordinates | `bathymetry_digitizer.py` |
| Simple PDF with XYZ text | `pdf_to_xyz.py` |
| Quick extraction without calibration | `pdf_to_xyz.py` |

## Usage Examples

### Bathymetric Survey Digitizer

**First time (with interactive calibration)**:
```bash
python bathymetry_digitizer.py --input survey.png --interactive-calib --outdir output/
```

**Subsequent runs**:
```bash
python bathymetry_digitizer.py --input survey.png --calib-json output/calibration.json --outdir results/
```

**With custom parameters**:
```bash
python bathymetry_digitizer.py \
    --input survey.pdf \
    --calib-json calibration.json \
    --outdir results/ \
    --dpi 600 \
    --min-depth 5 \
    --max-depth 30 \
    --crop-params 100,200,50,50 \
    --debug
```

**With filename containing spaces** (use quotes):
```bash
python bathymetry_digitizer.py \
    --input "survey 1 of 5.pdf" \
    --interactive-calib \
    --outdir output/
```

> **Note**: If your filename contains spaces, enclose it in quotes: `--input "file name.pdf"`

See [BATHYMETRY_GUIDE.md](BATHYMETRY_GUIDE.md) for complete documentation.

### Simple PDF Converter

### Basic Usage

```bash
python pdf_to_xyz.py input.pdf
```

This will create `input.xyz` in the same directory.

### Advanced Usage

```bash
# Specify output file
python pdf_to_xyz.py input.pdf -o output.xyz

# Use higher DPI for better OCR quality
python pdf_to_xyz.py input.pdf --dpi 600

# Disable specific OCR engines
python pdf_to_xyz.py input.pdf --no-paddleocr

# Enable verbose logging
python pdf_to_xyz.py input.pdf -v
```

### Command-Line Options

- `input_pdf`: Path to the input PDF file (required)
- `-o, --output`: Output XYZ file path (default: input_name.xyz)
- `--dpi`: DPI for PDF to image conversion (default: 300)
- `--no-tesseract`: Disable Tesseract OCR
- `--no-easyocr`: Disable EasyOCR
- `--no-paddleocr`: Disable PaddleOCR
- `-v, --verbose`: Enable verbose logging

See [QUICKSTART.md](QUICKSTART.md) for more details on the simple converter.

## Supported Data Formats (pdf_to_xyz.py)

The simple converter can recognize bathymetric data in various formats:

1. **Space-separated**: `X Y Z`
   ```
   123.456 78.901 -45.6
   ```

2. **Comma-separated**: `X,Y,Z` or `X, Y, Z`
   ```
   123.456, 78.901, -45.6
   ```

3. **Labeled coordinates**: `X: value Y: value Z: value`
   ```
   X: 123.456 Y: 78.901 Z: -45.6
   ```

4. **Lat/Lon/Depth format**:
   ```
   Latitude: 78.901 Longitude: 123.456 Depth: -45.6
   ```

## Output Formats

### Bathymetric Digitizer Output

The digitizer produces multiple output files:
- `output.xyz`: Calibrated XYZ point cloud
- `points_raw.csv`: All OCR detections
- `points_clean.csv`: Filtered and transformed points
- `debug_overlay.png`: Visual QA with bounding boxes
- `calibration.json`: Affine transformation parameters

### Simple Converter Output

The output XYZ file contains space-separated coordinates:

```
# X Y Z
# Total points: 100
123.456000 78.901000 -45.600000
124.567000 78.902000 -46.700000
...
```

## How the Bathymetric Digitizer Works

1. **Image Loading**: PDF/PNG → grayscale at specified DPI
2. **Cropping**: Automatic detection and removal of margins/title block
3. **Preprocessing**: Denoising → adaptive threshold → border removal
4. **OCR Detection**: Multiple PSM modes with bounding boxes
5. **Filtering**: Parse depths, range check, deduplication
6. **Calibration**: Interactive GCP selection or JSON loading
7. **Transformation**: Apply affine matrix to convert pixels → metres
8. **Export**: Write XYZ, CSVs, debug image with QC stats

## How the Simple Converter Works

1. **PDF to Image Conversion**: Converts each page to high-resolution images
2. **Image Preprocessing**: Enhances image quality through:
   - Grayscale conversion
   - Noise reduction
   - Adaptive thresholding
   - Automatic deskewing
3. **OCR Processing**: Extracts text using multiple OCR engines
4. **Data Parsing**: Identifies and extracts coordinate patterns
5. **Validation**: Validates coordinate ranges (lat/lon bounds)
6. **Export**: Saves to standard XYZ format

## OCR Engines

### Tesseract OCR
- Open-source OCR engine by Google
- Excellent for printed text
- Fast processing

### EasyOCR
- Deep learning-based OCR
- Good for various fonts and handwriting
- Supports 80+ languages

### PaddleOCR
- High-accuracy OCR from Baidu
- Excellent for complex layouts
- Superior handling of rotated/skewed text

The script automatically uses the best result from all available engines.

## Tips for Best Results

1. **Use High DPI**: For small or dense text, use `--dpi 600` or higher
2. **Clean Scans**: Ensure PDFs are clear and well-lit
3. **Orientation**: The script auto-deskews, but straight scans work best
4. **Multiple Engines**: Keep all OCR engines enabled for best accuracy
5. **Review Output**: Always verify the extracted coordinates

## Troubleshooting

### "Tesseract not available"
Install Tesseract OCR system package (see Prerequisites).

### "No bathymetric data found"
- Check if the PDF contains recognizable coordinate patterns
- Try increasing DPI: `--dpi 600`
- Ensure text is not in an image-only format without actual text

### Low accuracy
- Increase DPI for higher resolution
- Ensure source PDF quality is good
- Try different OCR engines if one fails

## Requirements

See `requirements.txt` for complete list of dependencies:
- pdf2image (PDF conversion)
- Pillow (Image processing)
- OpenCV (Image preprocessing)
- pytesseract (Tesseract OCR)
- easyocr (EasyOCR)
- paddleocr (PaddleOCR)
- pandas (Data handling)
- matplotlib (Interactive calibration)
- numpy (Numerical operations)

## Repository Structure

```
PDF-XYZ/
├── bathymetry_digitizer.py    # Production bathymetric survey digitizer
├── pdf_to_xyz.py              # Simple PDF to XYZ converter
├── test_bathymetry.py         # Tests for bathymetry digitizer
├── test_converter.py          # Tests for simple converter
├── example.py                 # Usage examples
├── requirements.txt           # Python dependencies
├── install.sh                 # Linux/macOS installation
├── install.bat                # Windows installation
├── BATHYMETRY_GUIDE.md       # Complete bathymetry digitizer guide
├── QUICKSTART.md             # Quick start for simple converter
├── CONTRIBUTING.md           # Contribution guidelines
└── README.md                 # This file
```

## Documentation

- **[BATHYMETRY_GUIDE.md](BATHYMETRY_GUIDE.md)**: Complete guide for the production bathymetric survey digitizer
- **[QUICKSTART.md](QUICKSTART.md)**: Quick start guide for the simple PDF converter
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Guidelines for contributing to the project

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.