#!/bin/bash
# Installation script for PDF-XYZ Converter

echo "=========================================="
echo "PDF-XYZ Converter Installation Script"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    OS="Other"
fi

echo "Detected OS: $OS"
echo ""

# Install system dependencies
echo "Step 1: Installing system dependencies..."
echo ""

if [ "$OS" == "Linux" ]; then
    echo "Installing Tesseract OCR and Poppler..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr poppler-utils
    echo "✓ System dependencies installed"
    
elif [ "$OS" == "macOS" ]; then
    echo "Installing Tesseract OCR and Poppler..."
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install tesseract poppler
    echo "✓ System dependencies installed"
    
else
    echo "Please install the following manually:"
    echo "  - Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
    echo "  - Poppler: https://github.com/oschwartz10612/poppler-windows/releases"
    echo ""
    read -p "Press Enter once you have installed these dependencies..."
fi

echo ""
echo "Step 2: Creating Python virtual environment..."
echo ""

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
if [ "$OS" == "Linux" ] || [ "$OS" == "macOS" ]; then
    source venv/bin/activate
else
    . venv/Scripts/activate
fi

echo "✓ Virtual environment created and activated"
echo ""

# Install Python dependencies
echo "Step 3: Installing Python dependencies..."
echo "This may take several minutes..."
echo ""

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Python dependencies installed"
echo ""

# Verify installation
echo "Step 4: Verifying installation..."
echo ""

python -c "import pytesseract; print('✓ Tesseract wrapper installed')" 2>/dev/null || echo "⚠ Tesseract wrapper not available"
python -c "import easyocr; print('✓ EasyOCR installed')" 2>/dev/null || echo "⚠ EasyOCR not available"
python -c "import paddleocr; print('✓ PaddleOCR installed')" 2>/dev/null || echo "⚠ PaddleOCR not available"
python -c "import cv2; print('✓ OpenCV installed')" 2>/dev/null || echo "✗ OpenCV not available"
python -c "from pdf2image import convert_from_path; print('✓ pdf2image installed')" 2>/dev/null || echo "✗ pdf2image not available"

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To use the converter:"
echo "  1. Activate the virtual environment:"
if [ "$OS" == "Linux" ] || [ "$OS" == "macOS" ]; then
    echo "     source venv/bin/activate"
else
    echo "     venv\\Scripts\\activate"
fi
echo "  2. Run the converter:"
echo "     python pdf_to_xyz.py your_file.pdf"
echo ""
echo "For more information, see README.md"
echo ""
