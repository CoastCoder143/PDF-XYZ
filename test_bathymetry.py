#!/usr/bin/env python3
"""
Test script for bathymetry digitizer core functions
Tests individual components without requiring actual images
"""

import sys
import json
import tempfile
from pathlib import Path

# Mock modules that might not be available
import numpy as np


def test_calibration_json():
    """Test calibration JSON loading and saving"""
    print("Testing calibration JSON format...")
    print("=" * 60)
    
    # Create test calibration
    affine_matrix = np.array([
        [1.5, 0.1, 72000.0],
        [0.1, -1.5, 19000.0]
    ])
    
    gcps = [
        {'pixel': [100, 100], 'real': [72150, 18850]},
        {'pixel': [1000, 100], 'real': [73500, 18850]},
        {'pixel': [100, 1000], 'real': [72150, 17500]}
    ]
    
    calib_data = {
        'affine_matrix': affine_matrix.tolist(),
        'gcps': gcps,
        'format': 'pixel_to_real',
        'units': 'metres'
    }
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(calib_data, f, indent=2)
        temp_path = f.name
    
    # Read back
    with open(temp_path, 'r') as f:
        loaded = json.load(f)
    
    # Verify
    loaded_matrix = np.array(loaded['affine_matrix'])
    assert loaded_matrix.shape == (2, 3), "Matrix shape incorrect"
    assert np.allclose(loaded_matrix, affine_matrix), "Matrix values incorrect"
    assert len(loaded['gcps']) == 3, "GCP count incorrect"
    
    print("✓ Calibration JSON format correct")
    print(f"  Matrix shape: {loaded_matrix.shape}")
    print(f"  GCPs: {len(loaded['gcps'])}")
    
    # Cleanup
    Path(temp_path).unlink()
    
    print("="*60)


def test_affine_transform():
    """Test affine transformation"""
    print("\nTesting affine transformation...")
    print("=" * 60)
    
    # Simple affine matrix: scale by 2, translate by (1000, 2000)
    affine_matrix = np.array([
        [2.0, 0.0, 1000.0],
        [0.0, 2.0, 2000.0]
    ])
    
    # Test points
    test_cases = [
        ([0, 0, 1], [1000, 2000]),
        ([100, 100, 1], [1200, 2200]),
        ([50, 25, 1], [1100, 2050])
    ]
    
    for pixel_coords, expected_real in test_cases:
        pixel = np.array(pixel_coords)
        real = affine_matrix @ pixel
        
        expected = np.array(expected_real)
        assert np.allclose(real, expected), f"Transform failed for {pixel_coords}"
        print(f"✓ Pixel {pixel_coords[:2]} → Real {real.tolist()}")
    
    print("="*60)


def test_crop_params_parsing():
    """Test crop parameter parsing"""
    print("\nTesting crop parameter parsing...")
    print("=" * 60)
    
    test_cases = [
        ("100,200,50,75", (100, 200, 50, 75)),
        ("10, 20, 30, 40", (10, 20, 30, 40)),
        ("0,0,0,0", (0, 0, 0, 0)),
        (None, None),
        ("invalid", None),
        ("10,20,30", None)
    ]
    
    def parse_crop_params(crop_str):
        """Simple parser for testing"""
        if not crop_str:
            return None
        try:
            parts = [int(x.strip()) for x in crop_str.split(',')]
            if len(parts) != 4:
                raise ValueError
            return tuple(parts)
        except (ValueError, AttributeError):
            return None
    
    for input_str, expected in test_cases:
        result = parse_crop_params(input_str)
        assert result == expected, f"Parse failed for {input_str}"
        print(f"✓ '{input_str}' → {result}")
    
    print("="*60)


def test_depth_filtering():
    """Test depth range filtering logic"""
    print("\nTesting depth filtering...")
    print("=" * 60)
    
    # Simulate detections
    detections = [
        {'text': '12.5', 'conf': 80},
        {'text': '15', 'conf': 75},
        {'text': '-5.0', 'conf': 70},  # Negative depth
        {'text': '100', 'conf': 85},   # Out of range
        {'text': 'X', 'conf': 60},     # Not a number
        {'text': '8', 'conf': 90},     # Single digit - will be rejected
        {'text': '25.3', 'conf': 65}
    ]
    
    min_depth = 0.0
    max_depth = 50.0
    min_token_length = 2  # Reject single characters
    
    accepted = []
    rejected_parse = 0
    rejected_range = 0
    rejected_short = 0
    
    for det in detections:
        text = det['text']
        
        # Reject single characters
        if len(text) < min_token_length:
            rejected_short += 1
            continue
        
        # Try to parse
        try:
            depth = float(text.replace(',', ''))
        except ValueError:
            rejected_parse += 1
            continue
        
        # Check range
        if not (min_depth <= depth <= max_depth):
            rejected_range += 1
            continue
        
        det['depth'] = depth
        accepted.append(det)
    
    print(f"Total detections: {len(detections)}")
    print(f"Accepted: {len(accepted)}")
    print(f"Rejected (short): {rejected_short}")
    print(f"Rejected (parse): {rejected_parse}")
    print(f"Rejected (range): {rejected_range}")
    
    assert len(accepted) == 3, f"Expected 3 accepted detections, got {len(accepted)}"
    assert rejected_short == 1, "Expected 1 short rejection"
    assert rejected_parse == 1, "Expected 1 parse rejection"
    assert rejected_range == 2, "Expected 2 range rejections"
    
    print("✓ Depth filtering logic correct")
    print("="*60)


def test_deduplication():
    """Test spatial deduplication logic"""
    print("\nTesting spatial deduplication...")
    print("=" * 60)
    
    # Simulate detections with centroids
    detections = [
        {'centroid': (100, 100), 'conf': 90, 'depth': 12.5},
        {'centroid': (105, 102), 'conf': 80, 'depth': 12.4},  # Near first, lower conf
        {'centroid': (200, 200), 'conf': 85, 'depth': 15.0},
        {'centroid': (202, 198), 'conf': 75, 'depth': 14.9},  # Near third, lower conf
        {'centroid': (300, 300), 'conf': 95, 'depth': 18.0}
    ]
    
    radius = 10  # pixels
    
    # Sort by confidence
    detections.sort(key=lambda x: x['conf'], reverse=True)
    
    accepted = []
    rejected_indices = set()
    
    for i, det in enumerate(detections):
        if i in rejected_indices:
            continue
        
        cx1, cy1 = det['centroid']
        accepted.append(det)
        
        # Mark nearby as duplicates
        for j in range(i + 1, len(detections)):
            if j in rejected_indices:
                continue
            
            cx2, cy2 = detections[j]['centroid']
            dist = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
            
            if dist < radius:
                rejected_indices.add(j)
    
    print(f"Original detections: {len(detections)}")
    print(f"After deduplication: {len(accepted)}")
    print(f"Removed duplicates: {len(rejected_indices)}")
    
    assert len(accepted) == 3, "Expected 3 unique detections"
    assert len(rejected_indices) == 2, "Expected 2 duplicates removed"
    
    # Verify highest confidence kept
    assert accepted[0]['conf'] == 95, "Highest confidence not first"
    
    print("✓ Deduplication logic correct")
    print("="*60)


def test_xyz_output_format():
    """Test XYZ file format generation"""
    print("\nTesting XYZ output format...")
    print("=" * 60)
    
    # Sample transformed detections
    detections = [
        {'x': 72345.678, 'y': 18912.345, 'depth': 12.5},
        {'x': 72346.890, 'y': 18913.456, 'depth': 13.2},
        {'x': 72348.123, 'y': 18914.789, 'depth': 11.8}
    ]
    
    # Generate XYZ format
    lines = ["# X (m)   Y (m)   Z (m)"]
    for det in detections:
        lines.append(f"{det['x']:.6f} {det['y']:.6f} {det['depth']:.6f}")
    
    xyz_content = '\n'.join(lines)
    
    print("Sample XYZ output:")
    print("-" * 60)
    print(xyz_content)
    print("-" * 60)
    
    # Verify format
    data_lines = xyz_content.split('\n')[1:]  # Skip header
    assert len(data_lines) == 3, "Expected 3 data lines"
    
    # Parse first line
    parts = data_lines[0].split()
    assert len(parts) == 3, "Expected 3 values per line"
    assert float(parts[0]) == 72345.678, "X value incorrect"
    assert float(parts[1]) == 18912.345, "Y value incorrect"
    assert float(parts[2]) == 12.5, "Z value incorrect"
    
    print("✓ XYZ format generation correct")
    print("="*60)


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print(" Bathymetry Digitizer - Test Suite")
    print("*" * 60)
    print("\n")
    
    try:
        test_calibration_json()
        test_affine_transform()
        test_crop_params_parsing()
        test_depth_filtering()
        test_deduplication()
        test_xyz_output_format()
        
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
