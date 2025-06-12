"""
Example usage of the get_context_from_docs function.

This script demonstrates how to use the document processor
in a FastAPI application or standalone context.
"""

import asyncio
from pathlib import Path
from typing import List
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from document_processor import get_context_from_docs, clean_text, get_text_summary


# FastAPI application setup
app = FastAPI(
    title="Document Context Extractor API",
    description="API for extracting text content from various document formats",
    version="1.0.0"
)


@app.post("/extract-context/")
async def extract_context_endpoint(files: List[UploadFile] = File(...)):
    """
    Extract text context from uploaded documents.
    
    Supports: PDF, DOCX, TXT, CSV, HTML, MD, Excel, Images (OCR)
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file sizes (limit to 10MB per file)
        max_size = 10 * 1024 * 1024  # 10MB
        for file in files:
            if hasattr(file, 'size') and file.size and file.size > max_size:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File {file.filename} is too large. Maximum size is 10MB."
                )
        
        # Extract context
        context = await get_context_from_docs(files)
        
        if not context or "No text content could be extracted" in context:
            raise HTTPException(
                status_code=422, 
                detail="Unable to extract text from any of the provided files"
            )
        
        # Clean the extracted text
        cleaned_context = clean_text(context)
        
        # Generate summary
        summary = get_text_summary(cleaned_context, max_length=200)
        
        return JSONResponse({
            "success": True,
            "files_processed": len(files),
            "context_length": len(cleaned_context),
            "summary": summary,
            "full_context": cleaned_context
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "document-context-extractor"}


@app.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats."""
    from document_processor import DocumentProcessor
    
    formats = {}
    for content_type, extensions in DocumentProcessor.SUPPORTED_FORMATS.items():
        formats[content_type] = extensions
    
    return {
        "supported_formats": formats,
        "notes": {
            "images": "Images require OCR processing (pytesseract)",
            "pdf": "Supports both PyPDF2 and pdfplumber",
            "office": "Supports modern Office formats (DOCX, XLSX)",
            "web": "HTML files are converted to plain text"
        }
    }


# Standalone usage example
async def standalone_example():
    """Example of using the function outside of FastAPI."""
    
    # Create mock UploadFile objects for demonstration
    class MockUploadFile:
        def __init__(self, filename: str, content: bytes, content_type: str = None):
            self.filename = filename
            self.content_type = content_type
            self._content = content
        
        async def read(self):
            return self._content
        
        async def seek(self, position: int):
            pass  # Mock implementation
    
    # Example with text files
    files = [
        MockUploadFile(
            "document1.txt",
            b"This is the content of the first document. It contains important information about our project.",
            "text/plain"
        ),
        MockUploadFile(
            "notes.md", 
            b"# Project Notes\n\n## Overview\nThis markdown file contains project notes and documentation.",
            "text/markdown"
        ),
        MockUploadFile(
            "data.csv",
            b"Name,Age,Department\nJohn Doe,30,Engineering\nJane Smith,25,Marketing\nBob Johnson,35,Sales",
            "text/csv"
        )
    ]
    
    print("Processing documents...")
    context = await get_context_from_docs(files)
    
    print("\n" + "="*60)
    print("EXTRACTED CONTEXT:")
    print("="*60)
    print(context)
    
    # Clean and summarize
    cleaned = clean_text(context)
    summary = get_text_summary(cleaned, max_length=150)
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(summary)


# Example with actual files
async def process_local_files(file_paths: List[str]):
    """Process actual local files."""
    
    class LocalUploadFile:
        def __init__(self, file_path: str):
            self.path = Path(file_path)
            self.filename = self.path.name
            self.content_type = None
            
            # Try to determine content type
            if self.path.suffix.lower() == '.pdf':
                self.content_type = 'application/pdf'
            elif self.path.suffix.lower() == '.docx':
                self.content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif self.path.suffix.lower() in ['.txt', '.log']:
                self.content_type = 'text/plain'
            elif self.path.suffix.lower() == '.csv':
                self.content_type = 'text/csv'
            elif self.path.suffix.lower() == '.html':
                self.content_type = 'text/html'
            elif self.path.suffix.lower() in ['.md', '.markdown']:
                self.content_type = 'text/markdown'
        
        async def read(self):
            return self.path.read_bytes()
        
        async def seek(self, position: int):
            pass
    
    # Validate files exist
    valid_files = []
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists() and path.is_file():
            valid_files.append(LocalUploadFile(file_path))
        else:
            print(f"Warning: File not found: {file_path}")
    
    if not valid_files:
        print("No valid files to process.")
        return
    
    print(f"Processing {len(valid_files)} files...")
    context = await get_context_from_docs(valid_files)
    
    print("\n" + "="*60)
    print("EXTRACTED CONTEXT FROM LOCAL FILES:")
    print("="*60)
    print(context)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Process command line file arguments
        file_paths = sys.argv[1:]
        print(f"Processing files: {file_paths}")
        asyncio.run(process_local_files(file_paths))
    else:
        # Run standalone example
        print("Running standalone example...")
        asyncio.run(standalone_example())
        
        print("\n" + "="*60)
        print("To run the FastAPI server:")
        print("python -m uvicorn example_usage:app --reload --port 8000")
        print("\nThen visit: http://localhost:8000/docs")
        print("="*60)