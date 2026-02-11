# Contributing to PDF-XYZ

Thank you for your interest in contributing to PDF-XYZ!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Sample PDF (if possible) or description of the input
- Error messages or logs
- Your environment (OS, Python version, dependency versions)

### Suggesting Enhancements

We welcome suggestions for:
- New coordinate formats to support
- Additional OCR engines
- Performance improvements
- Better preprocessing techniques
- Documentation improvements

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**:
   ```bash
   python test_converter.py
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/CoastCoder143/PDF-XYZ.git
   cd PDF-XYZ
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run tests:
   ```bash
   python test_converter.py
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular
- Comment complex logic

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test with various PDF formats
- Validate coordinate extraction accuracy

## Documentation

- Update README.md for user-facing changes
- Update QUICKSTART.md for setup changes
- Add docstrings for new functions/classes
- Include usage examples

## Areas for Contribution

### High Priority
- Support for more coordinate formats
- Better handling of rotated text
- Table extraction for structured data
- Batch processing improvements
- Error handling enhancements

### Medium Priority
- GUI interface
- Additional output formats (CSV, GeoJSON, etc.)
- Cloud OCR integration (Google Vision, AWS Textract)
- Performance optimization
- Better logging and progress tracking

### Low Priority
- Docker container
- Web service/API
- Configuration file support
- Coordinate transformation (projections)

## Questions?

Feel free to open an issue for any questions about contributing!
