# PDF-XYZ

Convert scanned PDF documents containing bathymetric data to XYZ format using advanced OCR technology.

## Features

- **Multiple OCR Engines**: Utilizes Tesseract, EasyOCR, and PaddleOCR for maximum accuracy
- **Advanced Image Preprocessing**: Automatic denoising, deskewing, and thresholding
- **Bathymetric Data Parsing**: Intelligently extracts X, Y, Z coordinates from various formats
- **High DPI Support**: Configurable resolution for optimal text recognition
- **Flexible Format Support**: Handles various coordinate formats and notations

## Installation

### Prerequisites

1. **System Dependencies** (for Tesseract OCR):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install tesseract-ocr poppler-utils
   
   # macOS
   brew install tesseract poppler
   
   # Windows
   # Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   # Download and install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
   ```

2. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

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

## Supported Data Formats

The script can recognize bathymetric data in various formats:

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

## Output Format

The output XYZ file contains space-separated coordinates:

```
# X Y Z
# Total points: 100
123.456000 78.901000 -45.600000
124.567000 78.902000 -46.700000
...
```

## How It Works

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
- PyMuPDF (PDF parsing)
- pandas (Data handling)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.