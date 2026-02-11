@echo off
REM Installation script for PDF-XYZ Converter (Windows)

echo ==========================================
echo PDF-XYZ Converter Installation Script
echo ==========================================
echo.

echo Step 1: System Dependencies
echo ==========================================
echo.
echo Please ensure you have installed:
echo   1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
echo   2. Poppler: https://github.com/oschwartz10612/poppler-windows/releases
echo.
echo After installation, add them to your PATH environment variable.
echo.
pause

echo.
echo Step 2: Creating Python virtual environment...
echo ==========================================
echo.

python -m venv venv

echo Virtual environment created.
echo.

echo Step 3: Installing Python dependencies...
echo ==========================================
echo This may take several minutes...
echo.

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Python dependencies installed.
echo.

echo Step 4: Verifying installation...
echo ==========================================
echo.

python -c "import pytesseract; print('✓ Tesseract wrapper installed')" 2>nul || echo ⚠ Tesseract wrapper not available
python -c "import easyocr; print('✓ EasyOCR installed')" 2>nul || echo ⚠ EasyOCR not available
python -c "import paddleocr; print('✓ PaddleOCR installed')" 2>nul || echo ⚠ PaddleOCR not available
python -c "import cv2; print('✓ OpenCV installed')" 2>nul || echo ✗ OpenCV not available
python -c "from pdf2image import convert_from_path; print('✓ pdf2image installed')" 2>nul || echo ✗ pdf2image not available

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo To use the converter:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo   2. Run the converter:
echo      python pdf_to_xyz.py your_file.pdf
echo.
echo For more information, see README.md
echo.
pause
