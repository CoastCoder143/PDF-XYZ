# PDF-XYZ

Advanced tools for digitizing bathymetric survey data from scanned documents.

## 🚀 Three Ways to Use This Tool

Choose the method that works best for you:

### 1. Configuration File (Best for Repeated Use) ⭐ **NEW**

**Set your input file once in a config file, then run:**

```bash
python run_from_config.py
```

Perfect for:
- 📋 **Documenting your workflow**
- 🔄 **Reusing the same settings**
- 📦 **Batch processing multiple files**
- 👥 **Sharing configurations with team**

📖 **[Complete Configuration Guide →](CONFIG_GUIDE.md)**

**Quick Setup:**
```bash
# 1. Copy a template
cp config_simple_example.json my_config.json

# 2. Edit my_config.json with your input file path
# 3. Run conversion
python run_from_config.py --config my_config.json
```

### 2. Interactive Mode (Easiest for Beginners)

**Just run one command and answer prompts:**

```bash
python convert.py
```

This interactive script will:
1. 📁 Help you select your input file
2. 🔧 Choose the right conversion tool
3. 📂 Set up output directory
4. ⚙️ Configure options with simple prompts
5. ✨ Process your file and save results

**No command-line arguments needed!** Perfect for one-off conversions.

### 3. Direct Command-Line (For Automation)

**For scripting and advanced users:**

```bash
# Simple converter
python pdf_to_xyz.py input.pdf

# Bathymetric digitizer
python bathymetry_digitizer.py --input survey.png --interactive-calib --outdir output/
```

Full control over all parameters via command-line arguments.

---

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

**Direct Command-Line Usage**:
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

**Direct Command-Line Usage**:
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

## Interactive Mode (Easiest Way!) 🎯

The `convert.py` script provides a user-friendly interactive interface - perfect for beginners or one-off conversions.

### How It Works

```bash
python convert.py
```

The script will guide you through:

**Step 1: Select Input File**
- Automatically lists PDF/PNG files in current directory
- Enter a number to select, or provide a file path
- Handles filenames with spaces automatically

**Step 2: Choose Conversion Tool**
- Option 1: Simple PDF Converter (for text-based PDFs)
- Option 2: Bathymetric Survey Digitizer (for scanned charts)
- Clear descriptions help you choose

**Step 3: Output Directory**
- Default: `./output/`
- Or specify your own

**Step 4: Configure Options**
- DPI setting (quality vs speed)
- Calibration file (for bathymetric digitizer)
- All with sensible defaults

**Step 5: Confirm & Process**
- Review your choices
- Press 'y' to proceed
- Watch the progress!

### Example Interactive Session

```
======================================================================
               PDF to XYZ Converter - Interactive Mode
======================================================================

----------------------------------------------------------------------
  Step 1: Select Input File
----------------------------------------------------------------------

Found 3 file(s) in current directory:
  1. survey_chart.pdf (1248.5 KB)
  2. bathymetric_data.pdf (892.1 KB)
  3. scan_001.png (2156.8 KB)

Options:
  - Enter a number (1-3) to select a file
  - Or enter a file path directly

Your choice: 1

✓ Selected: survey_chart.pdf

----------------------------------------------------------------------
  Step 2: Select Conversion Tool
----------------------------------------------------------------------

Which type of conversion do you need?

  1. Simple PDF Converter (pdf_to_xyz.py)
     - For PDFs with XYZ text data
     - Quick extraction without calibration

  2. Bathymetric Survey Digitizer (bathymetry_digitizer.py)
     - For professional hydrographic survey charts
     - Requires georeferencing calibration

Enter 1 or 2: 2

✓ Selected: Bathymetric Digitizer

[... continues with remaining steps ...]
```

### Benefits of Interactive Mode

✅ **No command-line knowledge needed**
✅ **File browser shows available files**
✅ **Guided tool selection**
✅ **Sensible defaults for all parameters**
✅ **Handles filenames with spaces**
✅ **Confirmation before processing**
✅ **Clear progress indicators**

Perfect for users who want simplicity without memorizing command-line arguments!

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

### "module 'cv2' has no attribute 'cvtColor'"

**Problem**: OpenCV imports but functions are missing.

**Solution**: Reinstall OpenCV cleanly:
```bash
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python
pip cache purge
pip install opencv-python
```

For servers/headless: use `opencv-python-headless` instead.

See [BATHYMETRY_GUIDE.md](BATHYMETRY_GUIDE.md) for detailed troubleshooting.

### "Tesseract not available"
Install Tesseract OCR system package (see Prerequisites).

### "No bathymetric data found"
- Check if the PDF contains recognizable coordinate patterns
- Try increasing DPI: `--dpi 600`
- Ensure text is not in an image-only format without actual text

### "libGL.so.1: cannot open shared object file"

**Problem**: Missing system graphics libraries.

**Solution for Ubuntu 22.04+**:
```bash
sudo apt-get install -y libgl1 libglib2.0-0
```

**Solution for headless/servers**:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### "Package 'libgl1-mesa-glx' has no installation candidate"

Use `libgl1` instead on Ubuntu 22.04+, or run `./install.sh` which auto-detects.

### Filename with Spaces Error

Wrap filenames in quotes:
```bash
python bathymetry_digitizer.py --input "survey 1 of 15.pdf" --interactive-calib --outdir output/
```

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