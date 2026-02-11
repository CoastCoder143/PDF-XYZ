#!/usr/bin/env python3
"""
Example usage of the PDF to XYZ converter
"""

from pdf_to_xyz import PDFToXYZConverter
import sys

def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    converter = PDFToXYZConverter()
    
    # Convert a PDF file
    pdf_path = "sample_bathymetric.pdf"
    output_path = "output.xyz"
    
    success = converter.convert(pdf_path, output_path)
    
    if success:
        print(f"✓ Successfully converted {pdf_path} to {output_path}")
    else:
        print(f"✗ Failed to convert {pdf_path}")


def example_high_dpi():
    """High DPI conversion for better quality"""
    print("\n" + "=" * 60)
    print("Example 2: High DPI Conversion")
    print("=" * 60)
    
    converter = PDFToXYZConverter()
    
    # Use 600 DPI for better quality
    success = converter.convert("sample.pdf", "high_quality.xyz", dpi=600)
    
    if success:
        print("✓ High DPI conversion completed")


def example_selective_ocr():
    """Using only specific OCR engines"""
    print("\n" + "=" * 60)
    print("Example 3: Selective OCR Engines")
    print("=" * 60)
    
    # Use only Tesseract and EasyOCR
    converter = PDFToXYZConverter(
        use_tesseract=True,
        use_easyocr=True,
        use_paddleocr=False
    )
    
    success = converter.convert("sample.pdf", "tesseract_only.xyz")
    
    if success:
        print("✓ Conversion with selective OCR completed")


def example_manual_processing():
    """Manual step-by-step processing"""
    print("\n" + "=" * 60)
    print("Example 4: Manual Processing")
    print("=" * 60)
    
    converter = PDFToXYZConverter()
    
    # Step 1: Convert PDF to images
    images = converter.pdf_to_images("sample.pdf", dpi=300)
    print(f"Converted to {len(images)} images")
    
    # Step 2: Process each image
    all_coords = []
    for i, image in enumerate(images):
        print(f"Processing page {i+1}...")
        text = converter.extract_text_from_image(image)
        coords = converter.parse_bathymetric_data(text)
        all_coords.extend(coords)
    
    # Step 3: Save results
    converter.save_to_xyz(all_coords, "manual_output.xyz")
    print(f"✓ Manual processing completed: {len(all_coords)} points")


def create_sample_data():
    """Create a sample text file with bathymetric data for testing"""
    sample_data = """
    Bathymetric Survey Data
    Survey Date: 2024-01-15
    
    Station 1:
    X: 123.456 Y: 45.678 Z: -12.5
    
    Station 2:
    Latitude: 45.679 Longitude: 123.457 Depth: -13.2
    
    Station 3:
    123.458, 45.680, -14.1
    
    Station 4:
    123.459 45.681 -15.3
    
    Additional Points:
    123.460 45.682 -16.2
    123.461 45.683 -17.1
    123.462 45.684 -18.0
    """
    
    with open("sample_data.txt", "w") as f:
        f.write(sample_data)
    
    print("\nCreated sample_data.txt with test bathymetric data")


if __name__ == "__main__":
    print("PDF to XYZ Converter - Example Usage\n")
    
    # Create sample data file
    create_sample_data()
    
    # Note: These examples require actual PDF files to work
    print("\nNote: Examples require actual PDF files.")
    print("To use with your own PDF:")
    print("  python pdf_to_xyz.py your_file.pdf\n")
    
    # Show code examples
    print("Code Example - Basic Usage:")
    print("-" * 60)
    print("""
from pdf_to_xyz import PDFToXYZConverter

# Create converter
converter = PDFToXYZConverter()

# Convert PDF to XYZ
converter.convert('bathymetric_data.pdf', 'output.xyz')
    """)
    
    print("\nCode Example - Advanced Usage:")
    print("-" * 60)
    print("""
from pdf_to_xyz import PDFToXYZConverter

# Create converter with specific OCR engines
converter = PDFToXYZConverter(
    use_tesseract=True,
    use_easyocr=True,
    use_paddleocr=False
)

# High DPI conversion
converter.convert('scan.pdf', 'high_quality.xyz', dpi=600)
    """)
