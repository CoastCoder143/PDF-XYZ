#!/usr/bin/env python3
"""
PDF-XYZ Interactive Converter
Simple one-command interface to convert scanned PDFs to XYZ format
"""

import os
import sys
import glob
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("\n" + "="*70)
    print(" "*15 + "PDF to XYZ Converter - Interactive Mode")
    print("="*70)
    print()

def print_section(title):
    """Print section header"""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)

def get_input_file():
    """Ask user for input file with helpful guidance"""
    print_section("Step 1: Select Input File")
    
    # Look for PDF files in current directory
    pdf_files = glob.glob("*.pdf") + glob.glob("*.PDF")
    png_files = glob.glob("*.png") + glob.glob("*.PNG")
    all_files = pdf_files + png_files
    
    if all_files:
        print(f"\nFound {len(all_files)} file(s) in current directory:")
        for i, file in enumerate(all_files, 1):
            file_size = os.path.getsize(file) / 1024  # KB
            print(f"  {i}. {file} ({file_size:.1f} KB)")
        
        print(f"\nOptions:")
        print(f"  - Enter a number (1-{len(all_files)}) to select a file")
        print(f"  - Or enter a file path directly")
        
        choice = input("\nYour choice: ").strip()
        
        # Check if it's a number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(all_files):
                return all_files[idx]
            else:
                print(f"Invalid number. Please choose 1-{len(all_files)}")
                return get_input_file()
        else:
            # Treat as file path
            if os.path.exists(choice):
                return choice
            else:
                print(f"File not found: {choice}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry == 'y':
                    return get_input_file()
                else:
                    sys.exit(0)
    else:
        print("\nNo PDF or PNG files found in current directory.")
        print("Please enter the full path to your file:")
        
        file_path = input("\nFile path: ").strip()
        
        # Remove quotes if present (for paths with spaces)
        file_path = file_path.strip('"').strip("'")
        
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"File not found: {file_path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                return get_input_file()
            else:
                sys.exit(0)

def select_tool():
    """Ask user which tool to use"""
    print_section("Step 2: Select Conversion Tool")
    
    print("\nWhich type of conversion do you need?")
    print()
    print("  1. Simple PDF Converter (pdf_to_xyz.py)")
    print("     - For PDFs with XYZ text data")
    print("     - Quick extraction without calibration")
    print("     - Uses OCR to extract coordinates")
    print()
    print("  2. Bathymetric Survey Digitizer (bathymetry_digitizer.py)")
    print("     - For professional hydrographic survey charts")
    print("     - Scanned charts with spot soundings")
    print("     - Requires georeferencing calibration")
    print("     - More advanced preprocessing")
    print()
    
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in ['1', '2']:
            return int(choice)
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_output_directory():
    """Ask user for output directory"""
    print_section("Step 3: Output Directory")
    
    default_dir = "output"
    print(f"\nWhere should the results be saved?")
    print(f"  - Press Enter to use default: ./{default_dir}/")
    print(f"  - Or enter a custom directory path")
    
    choice = input("\nOutput directory: ").strip()
    
    if not choice:
        return default_dir
    else:
        return choice

def get_optional_parameters(tool_type):
    """Ask for optional parameters"""
    print_section("Step 4: Optional Parameters")
    
    params = {}
    
    if tool_type == 1:
        # Simple PDF converter parameters
        print("\nOptional: Adjust DPI for image quality")
        print("  - Higher DPI = Better quality but slower")
        print("  - Default: 300 DPI")
        print("  - Recommended for poor quality scans: 600 DPI")
        
        dpi_input = input("\nDPI (press Enter for default 300): ").strip()
        if dpi_input and dpi_input.isdigit():
            params['dpi'] = int(dpi_input)
        else:
            params['dpi'] = 300
    
    elif tool_type == 2:
        # Bathymetric digitizer parameters
        print("\nDo you already have a calibration file?")
        print("  - If this is your first time, you'll use interactive calibration")
        print("  - If you have a calibration.json file, you can use it")
        
        has_calib = input("\nDo you have a calibration file? (y/n): ").strip().lower()
        
        if has_calib == 'y':
            calib_file = input("Enter calibration file path: ").strip().strip('"').strip("'")
            if os.path.exists(calib_file):
                params['calib_json'] = calib_file
                params['interactive_calib'] = False
            else:
                print(f"File not found: {calib_file}")
                print("Will use interactive calibration instead.")
                params['interactive_calib'] = True
        else:
            params['interactive_calib'] = True
        
        print("\nOptional: DPI for PDF rendering")
        dpi_input = input("DPI (press Enter for default 300): ").strip()
        if dpi_input and dpi_input.isdigit():
            params['dpi'] = int(dpi_input)
        else:
            params['dpi'] = 300
    
    return params

def run_simple_converter(input_file, output_dir, params):
    """Run the simple PDF to XYZ converter"""
    print_section("Running Simple PDF Converter")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine output filename
    input_name = Path(input_file).stem
    output_file = os.path.join(output_dir, f"{input_name}.xyz")
    
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_file}")
    print(f"DPI:    {params.get('dpi', 300)}")
    print("\nProcessing...")
    
    # Build command
    cmd = f'python3 pdf_to_xyz.py "{input_file}" -o "{output_file}"'
    if params.get('dpi'):
        cmd += f' --dpi {params["dpi"]}'
    
    print(f"\nExecuting: {cmd}\n")
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

def run_bathymetry_digitizer(input_file, output_dir, params):
    """Run the bathymetric survey digitizer"""
    print_section("Running Bathymetric Survey Digitizer")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_dir}/")
    print(f"DPI:    {params.get('dpi', 300)}")
    
    if params.get('interactive_calib'):
        print("Mode:   Interactive calibration")
        
        # Check for headless environment (skip check on macOS)
        import sys
        if sys.platform != 'darwin' and 'DISPLAY' not in os.environ and os.name != 'nt':
            print("\n" + "="*70)
            print("⚠ WARNING: HEADLESS ENVIRONMENT DETECTED")
            print("="*70)
            print("\nInteractive calibration requires a graphical display.")
            print("You are running in a headless environment (no DISPLAY set).")
            print("\nThis will likely fail. Consider:")
            print("  1. Use --calib-json with a pre-made calibration file")
            print("  2. Run this script on your local machine")
            print("  3. Enable X11 forwarding: ssh -X user@server")
            print("\nSee BATHYMETRY_GUIDE.md for details.")
            print("="*70)
            
            cont = input("\nDo you want to continue anyway? (y/n): ").strip().lower()
            if cont != 'y':
                print("\n✗ Cancelled by user")
                return False
        
        print("\n⚠ Interactive calibration requires matplotlib")
        print("You will be prompted to:")
        print("  1. Click on known ground control points")
        print("  2. Enter their real-world coordinates")
        print("  3. Use at least 3 points for best results")
    else:
        print(f"Calibration: {params.get('calib_json')}")
    
    print("\nProcessing...")
    
    # Build command
    cmd = f'python3 bathymetry_digitizer.py --input "{input_file}" --outdir "{output_dir}"'
    
    if params.get('interactive_calib'):
        cmd += ' --interactive-calib'
    elif params.get('calib_json'):
        cmd += f' --calib-json "{params["calib_json"]}"'
    
    if params.get('dpi'):
        cmd += f' --dpi {params["dpi"]}'
    
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
        if params.get('interactive_calib'):
            print("  - calibration.json (save this for future use!)")
        return True
    else:
        print("\n" + "="*70)
        print("✗ Conversion failed")
        print("="*70)
        return False

def main():
    """Main interactive flow"""
    try:
        print_header()
        
        # Step 1: Get input file
        input_file = get_input_file()
        print(f"\n✓ Selected: {input_file}")
        
        # Step 2: Select tool
        tool_type = select_tool()
        tool_name = "Simple Converter" if tool_type == 1 else "Bathymetric Digitizer"
        print(f"\n✓ Selected: {tool_name}")
        
        # Step 3: Get output directory
        output_dir = get_output_directory()
        print(f"\n✓ Output directory: {output_dir}")
        
        # Step 4: Get optional parameters
        params = get_optional_parameters(tool_type)
        
        # Confirm before processing
        print_section("Ready to Process")
        print(f"\nInput file:  {input_file}")
        print(f"Tool:        {tool_name}")
        print(f"Output dir:  {output_dir}")
        print(f"Parameters:  {params}")
        
        proceed = input("\nProceed with conversion? (y/n): ").strip().lower()
        
        if proceed != 'y':
            print("\nCancelled by user.")
            return
        
        # Run the appropriate tool
        if tool_type == 1:
            success = run_simple_converter(input_file, output_dir, params)
        else:
            success = run_bathymetry_digitizer(input_file, output_dir, params)
        
        # Final message
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
