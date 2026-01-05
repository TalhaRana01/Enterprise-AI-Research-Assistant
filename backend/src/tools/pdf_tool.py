"""PDF processing tool for LangChain agents."""

from typing import Optional
from pathlib import Path
from langchain.tools import tool
from pydantic import BaseModel, Field

from src.loaders import PDFLoader
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PDFProcessInput(BaseModel):
    """Input schema for PDF processing tool."""
    
    file_path: str = Field(
        description="Path to the PDF file to process"
    )
    extract_text: bool = Field(
        default=True,
        description="Whether to extract text from PDF (default: True)"
    )
    max_pages: Optional[int] = Field(
        default=None,
        description="Maximum number of pages to process (None = all pages)"
    )


@tool(args_schema=PDFProcessInput)
def pdf_process_tool(file_path: str, extract_text: bool = True, max_pages: Optional[int] = None) -> str:
    """
    Process and extract content from a PDF file.
    
    This tool loads a PDF file and extracts text content from it.
    Useful for processing research papers, documents, or any PDF files.
    
    Use this tool when:
    - User uploads a PDF file
    - User wants to extract text from PDF
    - User needs to process PDF documents
    
    Args:
        file_path: Path to the PDF file
        extract_text: Whether to extract text (default: True)
        max_pages: Maximum pages to process (None = all)
        
    Returns:
        Extracted text content from PDF
        
    Example:
        file_path="/path/to/paper.pdf"
        Returns extracted text content
    """
    try:
        logger.info(f"PDF processing tool called: file_path='{file_path}'")
        
        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            return f"Error: PDF file not found at '{file_path}'"
        
        if not path.suffix.lower() == ".pdf":
            return f"Error: File is not a PDF: '{file_path}'"
        
        # Initialize loader
        loader = PDFLoader()
        
        # Load PDF
        documents = loader.load(file_path)
        
        # Limit pages if specified
        if max_pages:
            documents = documents[:max_pages]
        
        if not documents:
            return f"No content extracted from PDF: '{file_path}'"
        
        # Extract text
        if extract_text:
            text_parts = [doc.page_content for doc in documents]
            text = "\n\n".join(text_parts)
            
            # Add metadata summary
            metadata_info = []
            for i, doc in enumerate(documents[:5], 1):  # First 5 pages metadata
                metadata = doc.metadata
                metadata_info.append(
                    f"Page {i}: {metadata.get('file_name', 'unknown')}"
                )
            
            result = (
                f"Extracted {len(documents)} pages from PDF:\n"
                f"File: {path.name}\n"
                f"Pages processed: {len(documents)}\n\n"
                f"Content:\n{text[:2000]}"  # First 2000 chars
            )
            
            if len(text) > 2000:
                result += f"\n\n... (truncated, total {len(text)} characters)"
            
            logger.info(f"PDF processed: {len(documents)} pages, {len(text)} chars")
            return result
        else:
            return f"PDF loaded: {len(documents)} pages (text extraction disabled)"
        
    except Exception as e:
        logger.error(f"PDF processing tool failed: {e}")
        return f"Error processing PDF: {str(e)}"


class PDFProcessTool:
    """
    Wrapper class for PDF processing tool.
    
    Provides additional methods and configuration options.
    """
    
    def __init__(self, use_pymupdf: bool = True):
        """
        Initialize PDF processing tool.
        
        Args:
            use_pymupdf: Use PyMuPDF (faster) instead of PyPDF
        """
        self.loader = PDFLoader(use_pymupdf=use_pymupdf)
        logger.info(f"PDFProcessTool initialized: use_pymupdf={use_pymupdf}")
    
    def process(self, file_path: str, max_pages: Optional[int] = None) -> list:
        """
        Process PDF and return Document objects.
        
        Args:
            file_path: Path to PDF file
            max_pages: Maximum pages to process
            
        Returns:
            List of Document objects
        """
        try:
            documents = self.loader.load(file_path)
            if max_pages:
                documents = documents[:max_pages]
            logger.info(f"Processed {len(documents)} pages")
            return documents
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract plain text from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text string
        """
        try:
            text = self.loader.extract_text_only(file_path)
            logger.info(f"Extracted {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    def get_tool(self):
        """Get LangChain tool instance."""
        return pdf_process_tool

