"""PDF document loader for processing PDF research papers."""

from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader

from src.utils.logger import get_logger
from src.config import settings

logger = get_logger(__name__)


class PDFLoader:
    """
    Load and process PDF documents.
    
    Supports:
    - Loading PDFs from file paths
    - Extracting text and metadata
    - Handling multiple pages
    """
    
    def __init__(self, use_pymupdf: bool = True):
        """
        Initialize PDF loader.
        
        Args:
            use_pymupdf: Use PyMuPDF (faster) instead of PyPDF
        """
        self.use_pymupdf = use_pymupdf
        logger.info(f"PDFLoader initialized (use_pymupdf={use_pymupdf})")
    
    def load(
        self,
        file_path: str,
        extract_metadata: bool = True
    ) -> List[Document]:
        """
        Load PDF document from file path.
        
        Args:
            file_path: Path to PDF file
            extract_metadata: Whether to extract PDF metadata
            
        Returns:
            List of Document objects (one per page)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If PDF loading fails
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            if not path.suffix.lower() == ".pdf":
                raise ValueError(f"File is not a PDF: {file_path}")
            
            logger.info(f"Loading PDF: {file_path}")
            
            # Choose loader based on preference
            if self.use_pymupdf:
                loader = PyMuPDFLoader(str(path))
            else:
                loader = PyPDFLoader(str(path))
            
            # Load documents
            documents = loader.load()
            
            # Add file metadata
            for doc in documents:
                doc.metadata.update({
                    "source_file": str(path),
                    "file_name": path.name,
                    "file_type": "pdf"
                })
            
            logger.info(f"Loaded {len(documents)} pages from PDF: {path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {e}")
            raise Exception(f"PDF loading failed: {str(e)}")
    
    def load_multiple(
        self,
        file_paths: List[str],
        extract_metadata: bool = True
    ) -> List[Document]:
        """
        Load multiple PDF files.
        
        Args:
            file_paths: List of PDF file paths
            extract_metadata: Whether to extract metadata
            
        Returns:
            Combined list of Document objects
        """
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = self.load(file_path, extract_metadata)
                all_documents.extend(documents)
            except Exception as e:
                logger.warning(f"Skipping PDF {file_path}: {e}")
                continue
        
        logger.info(f"Loaded {len(all_documents)} total pages from {len(file_paths)} PDFs")
        return all_documents
    
    def extract_text_only(self, file_path: str) -> str:
        """
        Extract plain text from PDF (without LangChain Document structure).
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Combined text from all pages
        """
        documents = self.load(file_path, extract_metadata=False)
        return "\n\n".join([doc.page_content for doc in documents])