# Configuration File Guide

## Overview

The configuration file approach allows you to specify all conversion parameters in a JSON file, making it easy to:
- **Reuse settings** for multiple conversions
- **Document your workflow** with saved configurations
- **Avoid command-line complexity** while maintaining full control
- **Batch process** multiple files with different settings

## Quick Start

### Step 1: Copy a Template

Choose the appropriate template for your use case:

```bash
# For simple PDF conversion
cp config_simple_example.json my_config.json

# For bathymetric digitizer (first time, with calibration)
cp config_bathymetry_interactive.json my_config.json

# For bathymetric digitizer (with existing calibration)
cp config_bathymetry_calibrated.json my_config.json
```

### Step 2: Edit Configuration

Open `my_config.json` and update the settings:

```json
{
  "input_file": "path/to/your/survey.pdf",
  "tool": "bathymetry",
  "output_directory": "results",
  
  "common_parameters": {
    "dpi": 600
  },
  
  "bathymetry_digitizer_parameters": {
    "interactive_calibration": true
  }
}
```

### Step 3: Run Conversion

```bash
python run_from_config.py --config my_config.json
```

Or use the default `config.json`:

```bash
python run_from_config.py
```

## Configuration File Format

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `input_file` | string | Path to PDF or PNG file | `"survey.pdf"` |
| `tool` | string | Converter type: "simple" or "bathymetry" | `"bathymetry"` |

### Optional Common Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `output_directory` | string | `"output"` | Directory for output files |
| `common_parameters.dpi` | integer | `300` | Resolution for PDF rendering |

### Simple Converter Parameters

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `simple_converter_parameters.output_file` | string | auto | Output filename (auto-generated if empty) |
| `simple_converter_parameters.use_tesseract` | boolean | `true` | Enable Tesseract OCR |
| `simple_converter_parameters.use_easyocr` | boolean | `true` | Enable EasyOCR |
| `simple_converter_parameters.use_paddleocr` | boolean | `true` | Enable PaddleOCR |
| `simple_converter_parameters.verbose` | boolean | `false` | Enable verbose logging |

### Bathymetry Digitizer Parameters

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `bathymetry_digitizer_parameters.interactive_calibration` | boolean | `false` | Use interactive calibration mode |
| `bathymetry_digitizer_parameters.calibration_file` | string | - | Path to calibration JSON (required if not interactive) |
| `bathymetry_digitizer_parameters.min_depth` | number | `0` | Minimum depth filter (meters) |
| `bathymetry_digitizer_parameters.max_depth` | number | `50` | Maximum depth filter (meters) |
| `bathymetry_digitizer_parameters.min_confidence` | number | `0` | Minimum OCR confidence (0-100) |
| `bathymetry_digitizer_parameters.crop_params` | string | - | Manual crop: "left,top,right,bottom" |
| `bathymetry_digitizer_parameters.auto_crop` | boolean | `true` | Automatically crop margins |
| `bathymetry_digitizer_parameters.debug` | boolean | `false` | Save debug images |

## Examples

### Example 1: Simple Conversion

**File: `config_quick.json`**
```json
{
  "input_file": "bathymetric_data.pdf",
  "tool": "simple",
  "output_directory": "results"
}
```

**Run:**
```bash
python run_from_config.py --config config_quick.json
```

### Example 2: High-Quality Conversion

**File: `config_highquality.json`**
```json
{
  "input_file": "scanned_survey.pdf",
  "tool": "simple",
  "output_directory": "high_quality_output",
  
  "common_parameters": {
    "dpi": 600
  },
  
  "simple_converter_parameters": {
    "verbose": true
  }
}
```

### Example 3: Bathymetric Survey - First Time

**File: `config_survey_new.json`**
```json
{
  "input_file": "survey_sheet_01.png",
  "tool": "bathymetry",
  "output_directory": "survey_01_output",
  
  "common_parameters": {
    "dpi": 300
  },
  
  "bathymetry_digitizer_parameters": {
    "interactive_calibration": true,
    "min_depth": 5,
    "max_depth": 25,
    "debug": true
  }
}
```

**Run:**
```bash
python run_from_config.py --config config_survey_new.json
```

This will:
1. Load the survey sheet
2. Prompt you to select ground control points
3. Create a calibration file
4. Process and save results

### Example 4: Bathymetric Survey - Reusing Calibration

**File: `config_survey_batch.json`**
```json
{
  "input_file": "survey_sheet_02.png",
  "tool": "bathymetry",
  "output_directory": "survey_02_output",
  
  "common_parameters": {
    "dpi": 300
  },
  
  "bathymetry_digitizer_parameters": {
    "interactive_calibration": false,
    "calibration_file": "survey_01_output/calibration.json",
    "min_depth": 5,
    "max_depth": 25
  }
}
```

**Run:**
```bash
python run_from_config.py --config config_survey_batch.json
```

This reuses the calibration from the first survey sheet.

## Batch Processing

Create multiple config files and process them in sequence:

```bash
#!/bin/bash
# batch_process.sh

for config in config_sheet_*.json; do
    echo "Processing $config..."
    python run_from_config.py --config "$config"
    echo "Done with $config"
    echo ""
done
```

Or create configs programmatically:

```python
import json

# Base configuration
base_config = {
    "tool": "bathymetry",
    "common_parameters": {"dpi": 300},
    "bathymetry_digitizer_parameters": {
        "interactive_calibration": false,
        "calibration_file": "calibration.json",
        "min_depth": 5,
        "max_depth": 30
    }
}

# Generate configs for multiple files
for i in range(1, 11):
    config = base_config.copy()
    config["input_file"] = f"survey_sheet_{i:02d}.pdf"
    config["output_directory"] = f"survey_{i:02d}_output"
    
    with open(f"config_sheet_{i:02d}.json", "w") as f:
        json.dump(config, f, indent=2)
```

## Advantages of Configuration Files

### 1. Documentation
Configuration files serve as documentation of your processing workflow:
```json
{
  "_project": "Coastal Survey 2024",
  "_date": "2024-01-15",
  "_notes": "Using 600 DPI for high accuracy",
  "input_file": "coastal_survey.pdf",
  "common_parameters": {
    "dpi": 600
  }
}
```

### 2. Version Control
Track changes to your processing parameters:
```bash
git add config.json
git commit -m "Increased DPI to 600 for better OCR accuracy"
```

### 3. Repeatability
Ensure consistent processing across multiple files or time periods.

### 4. Collaboration
Share configuration files with team members:
```bash
# Share your config
git push origin main

# Team member uses it
git pull origin main
python run_from_config.py
```

## Validation and Error Handling

The script validates your configuration and provides helpful error messages:

**Missing input file:**
```
Configuration Validation Errors:
  ✗ Input file not found: survey.pdf

Please fix the errors in your config.json file.
```

**Missing calibration:**
```
Configuration Validation Errors:
  ✗ Bathymetry tool requires either 'interactive_calibration': true 
    or 'calibration_file' path

Please fix the errors in your config.json file.
```

## Tips

1. **Start with Templates**: Use the example config files as starting points
2. **Comments**: Use fields starting with `_` for comments (they're ignored)
3. **Relative Paths**: Paths are relative to where you run the script
4. **Test First**: Try with `debug: true` to verify settings
5. **Save Calibrations**: Keep calibration files for reuse across similar sheets

## Comparison with Other Methods

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Interactive** (`convert.py`) | One-off conversions, beginners | Easy, guided | Manual each time |
| **Command-line** | Quick tests, automation | Direct, scriptable | Long commands |
| **Config File** | Repeated use, documentation | Reusable, documented | Initial setup |

## Troubleshooting

### "Configuration file not found"
- Check the path to your config file
- Use absolute paths if needed
- Default is `config.json` in current directory

### "Invalid JSON"
- Validate JSON syntax at jsonlint.com
- Check for missing commas, quotes, brackets
- Remove trailing commas

### "Input file not found"
- Use absolute path: `"/full/path/to/file.pdf"`
- Or ensure file is relative to where you run the script
- Check filename spelling and extension

## See Also

- **config.json** - Main template with all options
- **config_simple_example.json** - Simple converter template
- **config_bathymetry_interactive.json** - Interactive calibration template
- **config_bathymetry_calibrated.json** - Reusable calibration template
