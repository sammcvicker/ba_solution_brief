import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from io import BytesIO
import tempfile
from pathlib import Path

from fastapi import UploadFile
from document_processor import get_context_from_docs, DocumentProcessor, clean_text, get_text_summary


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class."""
    
    def test_supported_formats(self):
        """Test that all expected formats are supported."""
        processor = DocumentProcessor()
        expected_formats = ['txt', 'pdf', 'docx', 'xlsx', 'md', 'html', 'jpg', 'png']
        
        all_extensions = []
        for extensions in processor.SUPPORTED_FORMATS.values():
            all_extensions.extend(extensions)
        
        for fmt in expected_formats:
            assert fmt in all_extensions or fmt.upper() in all_extensions
    
    def test_extract_text_from_pdf_no_library(self):
        """Test PDF extraction when libraries are not available."""
        with patch('document_processor.PDF', None), \
             patch('document_processor.PyPDF2', None):
            
            with pytest.raises(ImportError) as exc_info:
                DocumentProcessor.extract_text_from_pdf(b"fake pdf content")
            
            assert "PDF processing libraries not installed" in str(exc_info.value)
    
    @patch('document_processor.PyPDF2')
    def test_extract_text_from_pdf_pypdf2(self, mock_pypdf2):
        """Test PDF extraction using PyPDF2."""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF text"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = DocumentProcessor.extract_text_from_pdf(b"fake pdf content")
        assert result == "Sample PDF text"
    
    def test_extract_text_from_docx_no_library(self):
        """Test DOCX extraction when library is not available."""
        with patch('document_processor.Document', None):
            with pytest.raises(ImportError) as exc_info:
                DocumentProcessor.extract_text_from_docx(b"fake docx content")
            
            assert "python-docx not installed" in str(exc_info.value)
    
    @patch('document_processor.Document')
    def test_extract_text_from_docx(self, mock_document):
        """Test DOCX extraction."""
        # Mock document structure
        mock_paragraph = Mock()
        mock_paragraph.text = "Sample paragraph text"
        
        mock_cell = Mock()
        mock_cell.text = "Cell data"
        
        mock_row = Mock()
        mock_row.cells = [mock_cell]
        
        mock_table = Mock()
        mock_table.rows = [mock_row]
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = [mock_table]
        
        mock_document.return_value = mock_doc
        
        result = DocumentProcessor.extract_text_from_docx(b"fake docx content")
        assert "Sample paragraph text" in result
        assert "Cell data" in result
    
    def test_extract_text_from_excel_no_library(self):
        """Test Excel extraction when library is not available."""
        with patch('document_processor.openpyxl', None):
            with pytest.raises(ImportError) as exc_info:
                DocumentProcessor.extract_text_from_excel(b"fake excel content")
            
            assert "openpyxl not installed" in str(exc_info.value)
    
    @patch('document_processor.openpyxl')
    def test_extract_text_from_excel(self, mock_openpyxl):
        """Test Excel extraction."""
        # Mock workbook structure
        mock_sheet = Mock()
        mock_sheet.iter_rows.return_value = [
            ("Header1", "Header2"),
            ("Data1", "Data2")
        ]
        
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_workbook.__getitem__.return_value = mock_sheet
        
        mock_openpyxl.load_workbook.return_value = mock_workbook
        
        result = DocumentProcessor.extract_text_from_excel(b"fake excel content")
        assert "Sheet1" in result
        assert "Header1 | Header2" in result
        assert "Data1 | Data2" in result
    
    def test_extract_text_from_image_no_library(self):
        """Test image extraction when libraries are not available."""
        with patch('document_processor.Image', None), \
             patch('document_processor.pytesseract', None):
            
            with pytest.raises(ImportError) as exc_info:
                DocumentProcessor.extract_text_from_image(b"fake image content")
            
            assert "PIL and pytesseract not installed" in str(exc_info.value)
    
    @patch('document_processor.pytesseract')
    @patch('document_processor.Image')
    def test_extract_text_from_image(self, mock_image_module, mock_pytesseract):
        """Test image OCR extraction."""
        mock_image = Mock()
        mock_image_module.open.return_value = mock_image
        mock_pytesseract.image_to_string.return_value = "  Extracted text from image  "
        
        result = DocumentProcessor.extract_text_from_image(b"fake image content")
        assert result == "Extracted text from image"
    
    def test_extract_text_from_html_with_beautifulsoup(self):
        """Test HTML extraction with BeautifulSoup."""
        html_content = b"""
        <html>
            <head><title>Test</title></head>
            <script>alert('test');</script>
            <body>
                <h1>Main Header</h1>
                <p>This is a paragraph.</p>
                <style>.test { color: red; }</style>
            </body>
        </html>
        """
        
        with patch('builtins.__import__') as mock_import:
            # Mock BeautifulSoup
            mock_bs = Mock()
            mock_soup = Mock()
            mock_soup.get_text.return_value = "Main Header\nThis is a paragraph."
            mock_soup.__call__.return_value = []  # No script/style elements
            mock_bs.return_value = mock_soup
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'bs4':
                    mock_module = Mock()
                    mock_module.BeautifulSoup = mock_bs
                    return mock_module
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            result = DocumentProcessor.extract_text_from_html(html_content)
            assert "Main Header" in result
            assert "This is a paragraph" in result


class TestGetContextFromDocs:
    """Test suite for the main get_context_from_docs function."""
    
    @pytest.mark.asyncio
    async def test_empty_files_list(self):
        """Test behavior with empty files list."""
        result = await get_context_from_docs([])
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_single_text_file(self):
        """Test processing a single text file."""
        file_content = b"This is a test document content."
        
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.read = AsyncMock(return_value=file_content)
        mock_file.seek = AsyncMock()
        
        result = await get_context_from_docs([mock_file])
        
        assert "test.txt" in result
        assert "This is a test document content." in result
        assert "Successfully processed 1 out of 1 files" in result
    
    @pytest.mark.asyncio
    async def test_multiple_files(self):
        """Test processing multiple files."""
        files = []
        
        # Text file
        mock_text_file = AsyncMock(spec=UploadFile)
        mock_text_file.filename = "document1.txt"
        mock_text_file.content_type = "text/plain"
        mock_text_file.read = AsyncMock(return_value=b"Content from text file")
        mock_text_file.seek = AsyncMock()
        files.append(mock_text_file)
        
        # CSV file
        mock_csv_file = AsyncMock(spec=UploadFile)
        mock_csv_file.filename = "data.csv"
        mock_csv_file.content_type = "text/csv"
        mock_csv_file.read = AsyncMock(return_value=b"Name,Age\nJohn,30\nJane,25")
        mock_csv_file.seek = AsyncMock()
        files.append(mock_csv_file)
        
        result = await get_context_from_docs(files)
        
        assert "document1.txt" in result
        assert "data.csv" in result
        assert "Content from text file" in result
        assert "John,30" in result
        assert "Successfully processed 2 out of 2 files" in result
    
    @pytest.mark.asyncio
    async def test_pdf_file_processing(self):
        """Test PDF file processing."""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"fake pdf content")
        mock_file.seek = AsyncMock()
        
        with patch.object(DocumentProcessor, 'extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Extracted PDF text content"
            
            result = await get_context_from_docs([mock_file])
            
            assert "document.pdf" in result
            assert "Extracted PDF text content" in result
            mock_extract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unsupported_file_fallback(self):
        """Test fallback behavior for unsupported file types."""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "unknown.xyz"
        mock_file.content_type = "application/unknown"
        mock_file.read = AsyncMock(return_value=b"Some text content")
        mock_file.seek = AsyncMock()
        
        result = await get_context_from_docs([mock_file])
        
        assert "unknown.xyz" in result
        assert "Some text content" in result
    
    @pytest.mark.asyncio
    async def test_file_processing_error_handling(self):
        """Test error handling during file processing."""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "error.txt"
        mock_file.content_type = "text/plain"
        mock_file.read = AsyncMock(side_effect=Exception("File read error"))
        mock_file.seek = AsyncMock()
        
        result = await get_context_from_docs([mock_file])
        
        # Should handle error gracefully
        assert "No text content could be extracted" in result
    
    @pytest.mark.asyncio
    async def test_mixed_success_failure_files(self):
        """Test processing with both successful and failed files."""
        files = []
        
        # Successful file
        mock_good_file = AsyncMock(spec=UploadFile)
        mock_good_file.filename = "good.txt"
        mock_good_file.content_type = "text/plain"
        mock_good_file.read = AsyncMock(return_value=b"Good content")
        mock_good_file.seek = AsyncMock()
        files.append(mock_good_file)
        
        # Failed file
        mock_bad_file = AsyncMock(spec=UploadFile)
        mock_bad_file.filename = "bad.txt"
        mock_bad_file.content_type = "text/plain"
        mock_bad_file.read = AsyncMock(side_effect=Exception("Error"))
        mock_bad_file.seek = AsyncMock()
        files.append(mock_bad_file)
        
        result = await get_context_from_docs(files)
        
        assert "good.txt" in result
        assert "Good content" in result
        assert "Successfully processed 1 out of 2 files" in result


class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_clean_text_whitespace(self):
        """Test cleaning excessive whitespace."""
        text = "This   has    excessive     whitespace\n\n\n\nand\tlines"
        result = clean_text(text)
        assert result == "This has excessive whitespace\n\nand lines"
    
    def test_clean_text_control_characters(self):
        """Test removing control characters."""
        text = "Normal text\x00with\x01control\x02chars"
        result = clean_text(text)
        assert result == "Normal textwithcontrolchars"
    
    def test_get_text_summary_short_text(self):
        """Test summary with text shorter than max length."""
        text = "This is a short text."
        result = get_text_summary(text, max_length=100)
        assert result == text
    
    def test_get_text_summary_long_text(self):
        """Test summary with text longer than max length."""
        text = "This is a very long text that should be truncated at some point because it exceeds the maximum length limit."
        result = get_text_summary(text, max_length=50)
        
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")
        assert result.startswith("This is a very long text")
    
    def test_get_text_summary_no_space_break(self):
        """Test summary when no space is found for break point."""
        text = "A" * 100
        result = get_text_summary(text, max_length=50)
        
        assert len(result) == 53  # 50 + "..."
        assert result == "A" * 50 + "..."


class TestIntegration:
    """Integration tests for the document processor."""
    
    @pytest.mark.asyncio
    async def test_real_file_processing(self):
        """Test processing with actual temporary files."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is test content from a real file.")
            temp_path = f.name
        
        try:
            # Create UploadFile-like object
            with open(temp_path, 'rb') as file:
                content = file.read()
            
            mock_file = AsyncMock(spec=UploadFile)
            mock_file.filename = Path(temp_path).name
            mock_file.content_type = "text/plain"
            mock_file.read = AsyncMock(return_value=content)
            mock_file.seek = AsyncMock()
            
            result = await get_context_from_docs([mock_file])
            
            assert "This is test content from a real file." in result
            assert Path(temp_path).name in result
            
        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)


# Pytest configuration
@pytest.fixture
def sample_upload_file():
    """Fixture providing a sample UploadFile mock."""
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "sample.txt"
    mock_file.content_type = "text/plain"
    mock_file.read = AsyncMock(return_value=b"Sample file content")
    mock_file.seek = AsyncMock()
    return mock_file


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])