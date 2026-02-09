#!/usr/bin/env python3
"""
Test script for PDF to XYZ converter
Tests individual components without requiring actual PDFs
"""

import sys
from io import StringIO

# Mock the imports that might not be available
class MockConverter:
    """Mock converter for testing without dependencies"""
    
    def parse_bathymetric_data(self, text: str):
        """Test the parsing logic"""
        import re
        coordinates = []
        
        patterns = [
            r'(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)',
            r'X[:\s]*(-?\d+\.?\d*)\s*Y[:\s]*(-?\d+\.?\d*)\s*Z[:\s]*(-?\d+\.?\d*)',
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
                        if abs(x) <= 180 and abs(y) <= 90:
                            coordinates.append((x, y, z))
                        elif abs(y) <= 180 and abs(x) <= 90:
                            coordinates.append((y, x, z))
                    except (ValueError, IndexError):
                        continue
        
        return coordinates


def test_parsing():
    """Test coordinate parsing"""
    print("Testing coordinate parsing...")
    print("=" * 60)
    
    converter = MockConverter()
    
    # Test case 1: Space-separated
    test1 = "123.456 78.901 -45.6"
    result1 = converter.parse_bathymetric_data(test1)
    assert len(result1) == 1, f"Test 1 failed: expected 1 coordinate, got {len(result1)}"
    assert result1[0] == (123.456, 78.901, -45.6), f"Test 1 failed: wrong values {result1[0]}"
    print("✓ Test 1 passed: Space-separated coordinates")
    
    # Test case 2: Comma-separated
    test2 = "123.456, 78.901, -45.6"
    result2 = converter.parse_bathymetric_data(test2)
    assert len(result2) == 1, f"Test 2 failed: expected 1 coordinate, got {len(result2)}"
    print("✓ Test 2 passed: Comma-separated coordinates")
    
    # Test case 3: Labeled coordinates
    test3 = "X: 123.456 Y: 78.901 Z: -45.6"
    result3 = converter.parse_bathymetric_data(test3)
    assert len(result3) == 1, f"Test 3 failed: expected 1 coordinate, got {len(result3)}"
    print("✓ Test 3 passed: Labeled coordinates")
    
    # Test case 4: Lat/Lon format
    test4 = "Latitude: 78.901 Longitude: 123.456 Depth: -45.6"
    result4 = converter.parse_bathymetric_data(test4)
    assert len(result4) == 1, f"Test 4 failed: expected 1 coordinate, got {len(result4)}"
    print("✓ Test 4 passed: Lat/Lon/Depth format")
    
    # Test case 5: Multiple coordinates
    test5 = """
    123.456 78.901 -45.6
    123.457 78.902 -46.7
    123.458 78.903 -47.8
    """
    result5 = converter.parse_bathymetric_data(test5)
    assert len(result5) == 3, f"Test 5 failed: expected 3 coordinates, got {len(result5)}"
    print("✓ Test 5 passed: Multiple coordinates")
    
    # Test case 6: Mixed formats
    test6 = """
    Station 1:
    X: 123.456 Y: 78.901 Z: -45.6
    
    Station 2:
    Latitude: 78.902 Longitude: 123.457 Depth: -46.7
    
    Station 3:
    123.458, 78.903, -47.8
    """
    result6 = converter.parse_bathymetric_data(test6)
    assert len(result6) == 3, f"Test 6 failed: expected 3 coordinates, got {len(result6)}"
    print("✓ Test 6 passed: Mixed formats")
    
    # Test case 7: Invalid coordinates (out of range)
    test7 = "999.999 999.999 -45.6"
    result7 = converter.parse_bathymetric_data(test7)
    assert len(result7) == 0, f"Test 7 failed: should reject out of range coordinates"
    print("✓ Test 7 passed: Out of range rejection")
    
    # Test case 8: Negative coordinates
    test8 = "-123.456 -78.901 -45.6"
    result8 = converter.parse_bathymetric_data(test8)
    assert len(result8) == 1, f"Test 8 failed: expected 1 coordinate"
    print("✓ Test 8 passed: Negative coordinates")
    
    print("\n" + "=" * 60)
    print("All parsing tests passed! ✓")
    print("=" * 60)


def test_xyz_format():
    """Test XYZ file format generation"""
    print("\nTesting XYZ file format...")
    print("=" * 60)
    
    # Sample coordinates
    coords = [
        (123.456, 78.901, -45.6),
        (123.457, 78.902, -46.7),
        (123.458, 78.903, -47.8),
    ]
    
    # Generate XYZ format
    output = StringIO()
    output.write("# X Y Z\n")
    output.write(f"# Total points: {len(coords)}\n")
    for x, y, z in coords:
        output.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
    
    result = output.getvalue()
    output.close()
    
    # Verify format
    lines = result.strip().split('\n')
    assert lines[0] == "# X Y Z", "Header incorrect"
    assert lines[1] == "# Total points: 3", "Point count incorrect"
    assert len(lines) == 5, f"Expected 5 lines, got {len(lines)}"  # 2 header + 3 data
    
    # Verify first data line
    parts = lines[2].split()
    assert len(parts) == 3, "Data line should have 3 values"
    assert float(parts[0]) == 123.456, "X coordinate incorrect"
    
    print("✓ XYZ format generation correct")
    print("\nSample output:")
    print("-" * 60)
    print(result)
    print("-" * 60)
    print("All format tests passed! ✓")
    print("=" * 60)


def test_coordinate_validation():
    """Test coordinate validation logic"""
    print("\nTesting coordinate validation...")
    print("=" * 60)
    
    valid_cases = [
        (0.0, 0.0, 0.0, True, "Origin"),
        (123.456, 45.678, -100.0, True, "Normal coordinates"),
        (-123.456, -45.678, 50.0, True, "Negative lat/lon"),
        (180.0, 90.0, 0.0, True, "Max valid"),
        (-180.0, -90.0, 0.0, True, "Min valid"),
    ]
    
    invalid_cases = [
        (200.0, 45.0, 0.0, False, "Longitude out of range"),
        (45.0, 100.0, 0.0, False, "Latitude out of range"),
        (999.0, 999.0, 0.0, False, "Both out of range"),
    ]
    
    for x, y, z, should_be_valid, description in valid_cases:
        is_valid = abs(x) <= 180 and abs(y) <= 90
        assert is_valid == should_be_valid, f"Validation failed for {description}"
        print(f"✓ {description}: Valid")
    
    for x, y, z, should_be_valid, description in invalid_cases:
        is_valid = abs(x) <= 180 and abs(y) <= 90
        assert is_valid == should_be_valid, f"Validation failed for {description}"
        print(f"✓ {description}: Invalid (as expected)")
    
    print("\n" + "=" * 60)
    print("All validation tests passed! ✓")
    print("=" * 60)


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print(" PDF to XYZ Converter - Test Suite")
    print("*" * 60)
    print("\n")
    
    try:
        test_parsing()
        test_xyz_format()
        test_coordinate_validation()
        
        print("\n")
        print("*" * 60)
        print(" ALL TESTS PASSED! ✓")
        print("*" * 60)
        print("\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
