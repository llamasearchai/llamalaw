"""
Document loading and preprocessing utilities
"""
import logging
import os
import re
from pathlib import Path
from typing import List, Optional, Union, Any

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not installed, PDF support will be limited")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not installed, DOCX support will be limited")


class DocumentLoader:
    """
    Utility for loading documents from various file formats
    """
    
    def __init__(self):
        """Initialize the document loader"""
        self.supported_extensions = ['.txt', '.pdf', '.docx']
        
    def load(self, file_path: Union[str, Path]) -> str:
        """
        Load a document and return its text content
        
        Args:
            file_path: Path to the document file
            
        Returns:
            str: Text content of the document
            
        Raises:
            ValueError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Get file extension
        file_ext = file_path.suffix.lower()
        
        # Load based on file type
        if file_ext == '.txt':
            return self._load_text(file_path)
        elif file_ext == '.pdf':
            return self._load_pdf(file_path)
        elif file_ext == '.docx':
            return self._load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
    def _load_text(self, file_path: Path) -> str:
        """Load text from a plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
            
    def _load_pdf(self, file_path: Path) -> str:
        """Load text from a PDF file"""
        if not PDF_AVAILABLE:
            logger.warning("PyPDF2 not installed, trying basic text extraction")
            # Basic fallback - try to read as text
            try:
                return self._load_text(file_path)
            except:
                raise ImportError("PyPDF2 is required for PDF support")
                
        text = []
        with open(file_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text.append(page.extract_text())
                
        return "\n\n".join(text)
        
    def _load_docx(self, file_path: Path) -> str:
        """Load text from a DOCX file"""
        if not DOCX_AVAILABLE:
            logger.warning("python-docx not installed, trying basic text extraction")
            # Basic fallback - try to read as text
            try:
                return self._load_text(file_path)
            except:
                raise ImportError("python-docx is required for DOCX support")
                
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
            
        return "\n".join(text)


class TextPreprocessor:
    """
    Utility for preprocessing document text
    """
    
    def __init__(self):
        """Initialize the text preprocessor"""
        pass
        
    def preprocess(self, text: str) -> str:
        """
        Preprocess text for analysis
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        # Remove excessive whitespace
        text = self._normalize_whitespace(text)
        
        # Remove headers/footers and page numbers (simplified version)
        text = self._remove_headers_footers(text)
        
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        return text
        
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with a maximum of two
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Trim whitespace at the beginning and end
        text = text.strip()
        
        return text
        
    def _remove_headers_footers(self, text: str) -> str:
        """Remove headers, footers, and page numbers"""
        # Simple heuristic: remove lines that might be page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Remove common footer patterns
        footer_patterns = [
            r'\n\s*Page \d+ of \d+\s*\n',
            r'\n\s*CONFIDENTIAL\s*\n',
            r'\n\s*\d+\s*\|\s*Page\s*\n',
        ]
        
        for pattern in footer_patterns:
            text = re.sub(pattern, '\n', text)
            
        return text
        
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors"""
        # Replace common OCR errors
        replacements = [
            (r'l\b', 'I'),      # Lowercase l at the end of a word is often a capital I
            (r'\bI([^a-zA-Z])', 'l\\1'),  # Capital I followed by non-letter is often lowercase L
            (r'0(?=\d{3})', 'O'),  # 0 followed by 3 digits might be O (in legal references)
            (r'(\d)O', '\\10'),  # Digit followed by O is often 0
            (r'rn', 'm'),      # 'rn' is often misread as 'm'
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
            
        return text 