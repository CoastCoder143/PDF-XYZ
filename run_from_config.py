#!/usr/bin/env python3
"""
Run PDF to XYZ Conversion from Configuration File

This script reads conversion parameters from config.json and runs the appropriate tool.
Perfect for users who want to:
- Avoid command-line arguments
- Reuse the same conversion settings
- Automate batch processing
- Keep conversion settings documented

Usage:
    python run_from_config.py
    python run_from_config.py --config custom_config.json
"""

import os
import sys
import json
import argparse
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("\n" + "="*70)
    print(" "*10 + "PDF-XYZ Converter - Configuration File Mode")
    print("="*70)
    print()

def load_config(config_path):
    """Load and validate configuration file"""
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        print("\nTo create a config file:")
        print("  1. Copy config.json to your desired location")
        print("  2. Edit the file with your settings")
        print("  3. Run: python run_from_config.py --config your_config.json")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)

def validate_config(config):
    """Validate configuration and provide helpful error messages"""
    errors = []
    
    # Check required fields
    if 'input_file' not in config or not config['input_file']:
        errors.append("'input_file' is required")
    elif not os.path.exists(config['input_file']):
        errors.append(f"Input file not found: {config['input_file']}")
    
    if 'tool' not in config or not config['tool']:
        errors.append("'tool' is required (must be 'simple' or 'bathymetry')")
    elif config['tool'] not in ['simple', 'bathymetry']:
        errors.append(f"Invalid tool: {config['tool']} (must be 'simple' or 'bathymetry')")
    
    # Tool-specific validation
    if config.get('tool') == 'bathymetry':
        bathy_params = config.get('bathymetry_digitizer_parameters', {})
        if not bathy_params.get('interactive_calibration', False):
            calib_file = bathy_params.get('calibration_file', '')
            if not calib_file:
                errors.append("Bathymetry tool requires either 'interactive_calibration': true or 'calibration_file' path")
            elif not os.path.exists(calib_file):
                errors.append(f"Calibration file not found: {calib_file}")
    
    if errors:
        print("\n" + "="*70)
        print("Configuration Validation Errors:")
        print("="*70)
        for error in errors:
            print(f"  ✗ {error}")
        print("\nPlease fix the errors in your config.json file.")
        print("="*70 + "\n")
        return False
    
    return True

def print_config_summary(config):
    """Print summary of configuration"""
    print("\n" + "-"*70)
    print("  Configuration Summary")
    print("-"*70)
    
    print(f"\nInput file:  {config['input_file']}")
    print(f"Tool:        {config['tool']}")
    print(f"Output dir:  {config.get('output_directory', 'output')}")
    
    common = config.get('common_parameters', {})
    print(f"DPI:         {common.get('dpi', 300)}")
    
    if config['tool'] == 'bathymetry':
        bathy = config.get('bathymetry_digitizer_parameters', {})
        print(f"Calibration: {'Interactive' if bathy.get('interactive_calibration') else bathy.get('calibration_file', 'N/A')}")
        if bathy.get('min_depth') or bathy.get('max_depth'):
            print(f"Depth range: {bathy.get('min_depth', 0)} to {bathy.get('max_depth', 50)} m")
    
    print("-"*70)

def run_simple_converter(config):
    """Run the simple PDF to XYZ converter"""
    print("\n" + "-"*70)
    print("  Running Simple PDF Converter")
    print("-"*70 + "\n")
    
    input_file = config['input_file']
    output_dir = config.get('output_directory', 'output')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get parameters
    common_params = config.get('common_parameters', {})
    simple_params = config.get('simple_converter_parameters', {})
    
    # Determine output file
    output_file = simple_params.get('output_file', '')
    if not output_file:
        input_name = Path(input_file).stem
        output_file = os.path.join(output_dir, f"{input_name}.xyz")
    else:
        output_file = os.path.join(output_dir, output_file)
    
    # Build command
    cmd = f'python3 pdf_to_xyz.py "{input_file}" -o "{output_file}"'
    
    # Add DPI
    dpi = common_params.get('dpi', 300)
    cmd += f' --dpi {dpi}'
    
    # Add OCR engine options
    if not simple_params.get('use_tesseract', True):
        cmd += ' --no-tesseract'
    if not simple_params.get('use_easyocr', True):
        cmd += ' --no-easyocr'
    if not simple_params.get('use_paddleocr', True):
        cmd += ' --no-paddleocr'
    
    # Add verbose flag
    if simple_params.get('verbose', False):
        cmd += ' -v'
    
    print(f"Executing: {cmd}\n")
    exit_code = os.system(cmd)
    
    if exit_code == 0:
        print("\n" + "="*70)
        print("✓ Conversion completed successfully!")
        print("="*70)
        print(f"\nOutput saved to: {output_file}")
        return True
    else:
        print("\n" + "="*70)
        print("✗ Conversion failed")
        print("="*70)
        return False

def run_bathymetry_digitizer(config):
    """Run the bathymetric survey digitizer"""
    print("\n" + "-"*70)
    print("  Running Bathymetric Survey Digitizer")
    print("-"*70 + "\n")
    
    input_file = config['input_file']
    output_dir = config.get('output_directory', 'output')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get parameters
    common_params = config.get('common_parameters', {})
    bathy_params = config.get('bathymetry_digitizer_parameters', {})
    
    # Build command
    cmd = f'python3 bathymetry_digitizer.py --input "{input_file}" --outdir "{output_dir}"'
    
    # Add calibration option
    if bathy_params.get('interactive_calibration', False):
        cmd += ' --interactive-calib'
        print("Mode: Interactive calibration")
        print("⚠ You will be prompted to select ground control points")
    else:
        calib_file = bathy_params.get('calibration_file', '')
        if calib_file:
            cmd += f' --calib-json "{calib_file}"'
            print(f"Calibration: {calib_file}")
    
    # Add DPI
    dpi = common_params.get('dpi', 300)
    cmd += f' --dpi {dpi}'
    
    # Add depth range
    if 'min_depth' in bathy_params:
        cmd += f' --min-depth {bathy_params["min_depth"]}'
    if 'max_depth' in bathy_params:
        cmd += f' --max-depth {bathy_params["max_depth"]}'
    
    # Add confidence threshold
    if 'min_confidence' in bathy_params:
        cmd += f' --min-conf {bathy_params["min_confidence"]}'
    
    # Add crop parameters
    crop_params = bathy_params.get('crop_params', '')
    if crop_params:
        cmd += f' --crop-params {crop_params}'
    
    # Add auto-crop flag
    if not bathy_params.get('auto_crop', True):
        cmd += ' --no-auto-crop'
    
    # Add debug flag
    if bathy_params.get('debug', False):
        cmd += ' --debug'
    
    print(f"\nExecuting: {cmd}\n")
    exit_code = os.system(cmd)
    
    if exit_code == 0:
        print("\n" + "="*70)
        print("✓ Conversion completed successfully!")
        print("="*70)
        print(f"\nOutputs saved to: {output_dir}/")
        print("  - output.xyz (point cloud)")
        print("  - points_raw.csv (all OCR candidates)")
        print("  - points_clean.csv (filtered points)")
        print("  - debug_overlay.png (visual QA)")
        if bathy_params.get('interactive_calibration'):
            print("  - calibration.json (save this for future use!)")
        return True
    else:
        print("\n" + "="*70)
        print("✗ Conversion failed")
        print("="*70)
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Run PDF to XYZ conversion from configuration file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Uses config.json
  %(prog)s --config my_config.json      # Uses custom config file
  
Configuration File Format:
  See config.json for a template with all available options.
  
  Minimum required fields:
    - input_file: Path to your PDF or PNG file
    - tool: "simple" or "bathymetry"
  
  For bathymetry tool, you also need:
    - interactive_calibration: true, OR
    - calibration_file: "path/to/calibration.json"
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Load configuration
    print(f"Loading configuration from: {args.config}")
    config = load_config(args.config)
    
    # Filter out comment fields (starting with _)
    config = {k: v for k, v in config.items() if not k.startswith('_')}
    
    # Validate configuration
    if not validate_config(config):
        sys.exit(1)
    
    # Print configuration summary
    print_config_summary(config)
    
    # Confirm before processing
    print("\nProceed with conversion? (y/n): ", end='')
    proceed = input().strip().lower()
    
    if proceed != 'y':
        print("\nCancelled by user.")
        return
    
    # Run appropriate tool
    try:
        if config['tool'] == 'simple':
            success = run_simple_converter(config)
        elif config['tool'] == 'bathymetry':
            success = run_bathymetry_digitizer(config)
        else:
            print(f"Unknown tool: {config['tool']}")
            sys.exit(1)
        
        if success:
            print("\n" + "="*70)
            print("  Done! Check the output directory for results.")
            print("="*70)
            print()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
