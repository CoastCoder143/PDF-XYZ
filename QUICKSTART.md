# Quick Start Guide

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CoastCoder143/PDF-XYZ.git
   cd PDF-XYZ
   ```

2. **Run installation script**:
   
   **Linux/macOS**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   
   **Windows**:
   ```cmd
   install.bat
   ```

3. **Activate virtual environment**:
   
   **Linux/macOS**:
   ```bash
   source venv/bin/activate
   ```
   
   **Windows**:
   ```cmd
   venv\Scripts\activate
   ```

## Basic Usage

Convert a PDF to XYZ format:
```bash
python pdf_to_xyz.py bathymetric_scan.pdf
```

This creates `bathymetric_scan.xyz` in the same directory.

## Advanced Examples

### Specify output file
```bash
python pdf_to_xyz.py input.pdf -o custom_output.xyz
```

### High-quality conversion (600 DPI)
```bash
python pdf_to_xyz.py scan.pdf --dpi 600
```

### Use specific OCR engines
```bash
# Only Tesseract
python pdf_to_xyz.py input.pdf --no-easyocr --no-paddleocr

# Only EasyOCR and PaddleOCR
python pdf_to_xyz.py input.pdf --no-tesseract
```

### Verbose output
```bash
python pdf_to_xyz.py input.pdf -v
```

## Python API

```python
from pdf_to_xyz import PDFToXYZConverter

# Create converter
converter = PDFToXYZConverter()

# Basic conversion
converter.convert('input.pdf', 'output.xyz')

# High DPI conversion
converter.convert('input.pdf', 'output.xyz', dpi=600)

# Custom OCR selection
converter = PDFToXYZConverter(
    use_tesseract=True,
    use_easyocr=True,
    use_paddleocr=False
)
converter.convert('input.pdf', 'output.xyz')
```

## Expected Input Format

Your PDF should contain bathymetric data in one of these formats:

- **Space-separated**: `123.456 78.901 -45.6`
- **Comma-separated**: `123.456, 78.901, -45.6`
- **Labeled**: `X: 123.456 Y: 78.901 Z: -45.6`
- **Lat/Lon**: `Latitude: 78.901 Longitude: 123.456 Depth: -45.6`

## Output Format

XYZ file with space-separated values:
```
# X Y Z
# Total points: 100
123.456000 78.901000 -45.600000
124.567000 78.902000 -46.700000
```

## Common Issues

### "Tesseract not found"
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### "No coordinates found"
- Increase DPI: `--dpi 600`
- Check if PDF contains text (not just images)
- Ensure coordinate format matches supported patterns

### Low quality results
- Use higher DPI
- Enable all OCR engines
- Ensure source PDF is clear and readable

## Performance Tips

1. **DPI Selection**:
   - 300 DPI: Fast, good for clear prints
   - 600 DPI: Better quality, slower
   - 1200 DPI: Highest quality, very slow

2. **OCR Engine Selection**:
   - All engines: Best accuracy, slowest
   - Tesseract only: Fastest
   - EasyOCR/PaddleOCR: Better for complex layouts

3. **Batch Processing**:
   ```bash
   for file in *.pdf; do
       python pdf_to_xyz.py "$file"
   done
   ```

## Getting Help

- Check the full documentation: `README.md`
- Run with verbose mode: `-v`
- View examples: `python example.py`

## System Requirements

- Python 3.7+
- 2GB RAM minimum (4GB+ recommended for large PDFs)
- Tesseract OCR installed
- Poppler utilities installed
