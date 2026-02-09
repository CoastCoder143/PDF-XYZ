#!/usr/bin/env python3
"""
PDF to XYZ Converter with Advanced OCR
Converts scanned PDF documents containing bathymetric data to .xyz format
Uses multiple OCR technologies for best results
"""

import os
import sys
import argparse
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Image and PDF processing
try:
    from pdf2image import convert_from_path
    import cv2
    import numpy as np
    from PIL import Image
    import fitz  # PyMuPDF
    import pdfplumber
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)

# OCR engines
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: Tesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not available")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("Warning: PaddleOCR not available")

import pandas as pd
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFToXYZConverter:
    """
    Advanced PDF to XYZ converter with multiple OCR engines
    """
    
    def __init__(self, use_tesseract=True, use_easyocr=True, use_paddleocr=True):
        """
        Initialize the converter with specified OCR engines
        
        Args:
            use_tesseract: Enable Tesseract OCR
            use_easyocr: Enable EasyOCR
            use_paddleocr: Enable PaddleOCR
        """
        self.use_tesseract = use_tesseract and TESSERACT_AVAILABLE
        self.use_easyocr = use_easyocr and EASYOCR_AVAILABLE
        self.use_paddleocr = use_paddleocr and PADDLEOCR_AVAILABLE
        
        # Initialize OCR readers
        if self.use_easyocr:
            logger.info("Initializing EasyOCR...")
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
        
        if self.use_paddleocr:
            logger.info("Initializing PaddleOCR...")
            self.paddleocr_reader = PaddleOCR(use_angle_cls=True, lang='en', 
                                             use_gpu=False, show_log=False)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Deskew if needed
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            if abs(angle) > 0.5:  # Only deskew if angle is significant
                (h, w) = thresh.shape
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                thresh = cv2.warpAffine(
                    thresh, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
        
        return thresh
    
    def extract_text_tesseract(self, image: np.ndarray) -> str:
        """
        Extract text using Tesseract OCR
        
        Args:
            image: Input image
            
        Returns:
            Extracted text
        """
        if not self.use_tesseract:
            return ""
        
        try:
            # Configure Tesseract for best results
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            logger.warning(f"Tesseract OCR failed: {e}")
            return ""
    
    def extract_text_easyocr(self, image: np.ndarray) -> str:
        """
        Extract text using EasyOCR
        
        Args:
            image: Input image
            
        Returns:
            Extracted text
        """
        if not self.use_easyocr:
            return ""
        
        try:
            results = self.easyocr_reader.readtext(image, detail=0, paragraph=True)
            return '\n'.join(results)
        except Exception as e:
            logger.warning(f"EasyOCR failed: {e}")
            return ""
    
    def extract_text_paddleocr(self, image: np.ndarray) -> str:
        """
        Extract text using PaddleOCR
        
        Args:
            image: Input image
            
        Returns:
            Extracted text
        """
        if not self.use_paddleocr:
            return ""
        
        try:
            results = self.paddleocr_reader.ocr(image, cls=True)
            if results and results[0]:
                text = '\n'.join([line[1][0] for line in results[0]])
                return text
            return ""
        except Exception as e:
            logger.warning(f"PaddleOCR failed: {e}")
            return ""
    
    def extract_text_from_image(self, image: np.ndarray) -> str:
        """
        Extract text from image using all available OCR engines and combine results
        
        Args:
            image: Input image
            
        Returns:
            Combined extracted text
        """
        preprocessed = self.preprocess_image(image)
        
        texts = []
        
        # Try all OCR engines
        if self.use_tesseract:
            logger.info("Running Tesseract OCR...")
            text = self.extract_text_tesseract(preprocessed)
            if text:
                texts.append(("tesseract", text))
        
        if self.use_easyocr:
            logger.info("Running EasyOCR...")
            text = self.extract_text_easyocr(preprocessed)
            if text:
                texts.append(("easyocr", text))
        
        if self.use_paddleocr:
            logger.info("Running PaddleOCR...")
            text = self.extract_text_paddleocr(preprocessed)
            if text:
                texts.append(("paddleocr", text))
        
        # Combine results - use the longest/most complete result
        if not texts:
            return ""
        
        # For now, use the result with most content
        best_text = max(texts, key=lambda x: len(x[1]))
        logger.info(f"Best OCR result from: {best_text[0]}")
        
        return best_text[1]
    
    def pdf_to_images(self, pdf_path: str, dpi: int = 300) -> List[np.ndarray]:
        """
        Convert PDF to images
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion
            
        Returns:
            List of images as numpy arrays
        """
        logger.info(f"Converting PDF to images at {dpi} DPI...")
        
        try:
            # Use pdf2image for conversion
            images = convert_from_path(pdf_path, dpi=dpi)
            
            # Convert to numpy arrays
            np_images = []
            for img in images:
                np_img = np.array(img)
                np_images.append(np_img)
            
            logger.info(f"Converted {len(np_images)} pages to images")
            return np_images
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            return []
    
    def parse_bathymetric_data(self, text: str) -> List[Tuple[float, float, float]]:
        """
        Parse bathymetric data (X, Y, Z coordinates) from extracted text
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            List of (X, Y, Z) tuples
        """
        logger.info("Parsing bathymetric data...")
        
        coordinates = []
        
        # Pattern to match coordinates
        # This matches various formats:
        # - Space/tab separated: X Y Z
        # - Comma separated: X,Y,Z or X, Y, Z
        # - With labels: X: value Y: value Z: value
        
        # Try different patterns
        patterns = [
            # Three numbers separated by spaces/tabs/commas
            r'(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)',
            # With coordinate labels
            r'X[:\s]*(-?\d+\.?\d*)\s*Y[:\s]*(-?\d+\.?\d*)\s*Z[:\s]*(-?\d+\.?\d*)',
            # Latitude/Longitude/Depth format
            r'(?:Lat|Latitude)[:\s]*(-?\d+\.?\d*)\s*(?:Lon|Longitude)[:\s]*(-?\d+\.?\d*)\s*(?:Depth|D)[:\s]*(-?\d+\.?\d*)',
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        x, y, z = float(match[0]), float(match[1]), float(match[2])
                        # Basic validation - coordinates should be reasonable
                        # Latitude: -90 to 90, Longitude: -180 to 180, Depth: typically negative or positive
                        if abs(x) <= 180 and abs(y) <= 90:
                            coordinates.append((x, y, z))
                        elif abs(y) <= 180 and abs(x) <= 90:
                            # Swap if order is reversed
                            coordinates.append((y, x, z))
                    except (ValueError, IndexError):
                        continue
        
        logger.info(f"Found {len(coordinates)} coordinate points")
        return coordinates
    
    def save_to_xyz(self, coordinates: List[Tuple[float, float, float]], 
                    output_path: str) -> bool:
        """
        Save coordinates to XYZ file format
        
        Args:
            coordinates: List of (X, Y, Z) tuples
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        if not coordinates:
            logger.error("No coordinates to save")
            return False
        
        try:
            with open(output_path, 'w') as f:
                # Write header
                f.write("# X Y Z\n")
                f.write(f"# Total points: {len(coordinates)}\n")
                
                # Write coordinates
                for x, y, z in coordinates:
                    f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
            
            logger.info(f"Successfully saved {len(coordinates)} points to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save XYZ file: {e}")
            return False
    
    def convert(self, pdf_path: str, output_path: Optional[str] = None, 
                dpi: int = 300) -> bool:
        """
        Main conversion function
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output XYZ file (optional)
            dpi: DPI for PDF to image conversion
            
        Returns:
            True if successful, False otherwise
        """
        # Validate input
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        # Set default output path
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_path = f"{pdf_name}.xyz"
        
        logger.info(f"Converting {pdf_path} to {output_path}")
        
        # Convert PDF to images
        images = self.pdf_to_images(pdf_path, dpi=dpi)
        if not images:
            return False
        
        # Process each page
        all_coordinates = []
        for i, image in enumerate(tqdm(images, desc="Processing pages")):
            logger.info(f"Processing page {i+1}/{len(images)}")
            
            # Extract text
            text = self.extract_text_from_image(image)
            
            if text:
                # Parse coordinates
                coordinates = self.parse_bathymetric_data(text)
                all_coordinates.extend(coordinates)
        
        # Save results
        if all_coordinates:
            return self.save_to_xyz(all_coordinates, output_path)
        else:
            logger.error("No bathymetric data found in PDF")
            return False


def main():
    """
    Main function for command-line usage
    """
    parser = argparse.ArgumentParser(
        description='Convert scanned PDF with bathymetric data to XYZ format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf
  %(prog)s input.pdf -o output.xyz
  %(prog)s input.pdf --dpi 600
  %(prog)s input.pdf --no-paddleocr
        """
    )
    
    parser.add_argument('input_pdf', help='Input PDF file path')
    parser.add_argument('-o', '--output', help='Output XYZ file path')
    parser.add_argument('--dpi', type=int, default=300, 
                       help='DPI for PDF to image conversion (default: 300)')
    parser.add_argument('--no-tesseract', action='store_true',
                       help='Disable Tesseract OCR')
    parser.add_argument('--no-easyocr', action='store_true',
                       help='Disable EasyOCR')
    parser.add_argument('--no-paddleocr', action='store_true',
                       help='Disable PaddleOCR')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create converter
    converter = PDFToXYZConverter(
        use_tesseract=not args.no_tesseract,
        use_easyocr=not args.no_easyocr,
        use_paddleocr=not args.no_paddleocr
    )
    
    # Convert
    success = converter.convert(args.input_pdf, args.output, args.dpi)
    
    if success:
        logger.info("Conversion completed successfully!")
        return 0
    else:
        logger.error("Conversion failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
