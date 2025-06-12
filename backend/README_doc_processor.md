# Document Context Extractor

A robust Python library for extracting text content from various document formats including PDF, DOCX, Excel, images (OCR), HTML, Markdown, and more.

## Features

- **Multi-format Support**: PDF, DOCX, XLSX, TXT, CSV, HTML, MD, Images (OCR)
- **FastAPI Integration**: Ready-to-use endpoint for document processing
- **Error Handling**: Graceful handling of corrupted files and missing dependencies
- **Text Cleaning**: Built-in utilities for cleaning and summarizing extracted text
- **Comprehensive Testing**: Full test suite with mocks and integration tests
- **Flexible Architecture**: Can be used standalone or as part of a web service

## Supported File Formats

| Format | Extensions | Library Used | Notes |
|--------|------------|--------------|-------|
| PDF | `.pdf` | PyPDF2, pdfplumber | Prefers pdfplumber for better text extraction |
| Word | `.docx` | python-docx | Extracts text from paragraphs and tables |
| Excel | `.xlsx`, `.xls` | openpyxl | Processes all sheets and formats as tables |
| Text | `.txt`, `.log`, `.csv` | Built-in | Direct text extraction |
| HTML | `.html`, `.htm` | BeautifulSoup4 | Strips tags and extracts clean text |
| Markdown | `.md`, `.markdown` | markdown | Converts to HTML then to text |
| Images | `.jpg`, `.png`, `.gif`, `.bmp` | PIL + pytesseract | OCR text extraction |

## Installation

### Basic Installation

```bash
pip install -r requirements_doc_processor.txt
```

### System Dependencies

For OCR functionality (image processing), you'll need to install Tesseract:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Quick Start

### Standalone Usage

```python
import asyncio
from document_processor import get_context_from_docs
from fastapi import UploadFile

# Your file processing code here
files = [...]  # List of UploadFile objects
context = await get_context_from_docs(files)
print(context)
```

### FastAPI Integration

```python
from fastapi import FastAPI, UploadFile, File
from document_processor import get_context_from_docs

app = FastAPI()

@app.post("/extract-context/")
async def extract_context(files: List[UploadFile] = File(...)):
    context = await get_context_from_docs(files)
    return {"context": context}
```

### Running the Example Server

```bash
python -m uvicorn example_usage:app --reload --port 8000
```

Then visit: http://localhost:8000/docs for the interactive API documentation.

## Command Line Usage

Process local files directly:

```bash
python example_usage.py file1.pdf file2.docx file3.txt
```

## API Reference

### Main Function

#### `get_context_from_docs(files: List[UploadFile]) -> str`

Extracts and consolidates text content from multiple uploaded files.

**Parameters:**
- `files`: List of FastAPI UploadFile objects

**Returns:**
- `str`: Consolidated text content with file headers and metadata

**Example:**
```python
context = await get_context_from_docs([upload_file1, upload_file2])
```

### Utility Functions

#### `clean_text(text: str) -> str`

Cleans and normalizes extracted text by removing excessive whitespace and control characters.

#### `get_text_summary(text: str, max_length: int = 500) -> str`

Generates a summary/preview of the extracted text, truncated at the specified length.

### DocumentProcessor Class

Low-level class for format-specific text extraction:

- `extract_text_from_pdf(content: bytes) -> str`
- `extract_text_from_docx(content: bytes) -> str`
- `extract_text_from_excel(content: bytes) -> str`
- `extract_text_from_image(content: bytes) -> str`
- `extract_text_from_html(content: bytes) -> str`

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest test_document_processor.py -v

# Run specific test categories
pytest test_document_processor.py::TestDocumentProcessor -v
pytest test_document_processor.py::TestGetContextFromDocs -v
```

### Test Coverage

The test suite includes:
- Unit tests for each document format processor
- Integration tests with real file processing
- Error handling and edge case testing
- Mock-based testing for external dependencies
- Async function testing

## Error Handling

The library includes comprehensive error handling:

1. **Missing Dependencies**: Graceful fallback when optional libraries aren't installed
2. **File Corruption**: Continues processing other files if one fails
3. **Encoding Issues**: Uses error-tolerant UTF-8 decoding
4. **Empty Files**: Handles files with no extractable content
5. **Network Issues**: Timeout handling for large file processing

## Configuration

### File Size Limits

Configure maximum file sizes in your FastAPI application:

```python
@app.post("/extract-context/")
async def extract_context(files: List[UploadFile] = File(...)):
    max_size = 10 * 1024 * 1024  # 10MB
    for file in files:
        if file.size and file.size > max_size:
            raise HTTPException(413, "File too large")
```

### OCR Configuration

Configure Tesseract OCR options:

```python
import pytesseract

# Set custom config
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
```

## Performance Considerations

1. **Large Files**: Consider streaming for files > 100MB
2. **OCR Processing**: Image processing is CPU-intensive
3. **Memory Usage**: PDF processing can use significant memory
4. **Concurrency**: Process multiple files concurrently when possible

## Common Issues

### Tesseract Not Found
```
TesseractNotFoundError: tesseract is not installed
```
**Solution**: Install Tesseract OCR system package

### PDF Extraction Empty
Some PDFs may return empty text if they're image-based or have unusual formatting.
**Solution**: Consider using OCR on PDF pages or alternative PDF libraries

### Memory Issues with Large Files
**Solution**: Implement file size limits or streaming processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Dependencies

See `requirements_doc_processor.txt` for the complete list of dependencies.

### Core Dependencies
- FastAPI: Web framework
- PyPDF2/pdfplumber: PDF processing
- python-docx: Word document processing
- openpyxl: Excel processing
- Pillow + pytesseract: Image OCR
- BeautifulSoup4: HTML processing
- markdown: Markdown processing

## Support

For issues and questions:
1. Check the test suite for usage examples
2. Review the example_usage.py file
3. Check error logs for specific dependency issues