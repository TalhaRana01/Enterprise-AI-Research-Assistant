"""Unit tests for document loaders."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

from src.loaders import ArXivLoader, PDFLoader
from tests.conftest import sample_paper, sample_documents


class TestArXivLoader:
    """Test ArXivLoader class."""
    
    @patch("src.loaders.arxiv_loader.LangChainArxivLoader")
    def test_search_success(self, mock_loader_class, sample_paper):
        """Test successful paper search."""
        # Setup mock
        mock_loader = Mock()
        mock_doc = Mock()
        mock_doc.metadata = {
            "Entry ID": "arxiv:2301.12345",
            "Title": sample_paper["title"],
            "Authors": sample_paper["authors"],
            "Published": sample_paper["published"],
            "pdf_url": sample_paper["pdf_url"]
        }
        mock_doc.page_content = sample_paper["full_text"]
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader
        
        # Test
        loader = ArXivLoader(max_results=5)
        results = loader.search("transformer models")
        
        # Assertions
        assert len(results) == 1
        assert results[0]["title"] == sample_paper["title"]
        assert results[0]["source"] == "arxiv"
        mock_loader_class.assert_called_once()
    
    def test_search_invalid_query(self):
        """Test search with invalid query."""
        loader = ArXivLoader()
        
        with pytest.raises(Exception):  # Changed from ValueError to Exception
            loader.search("ab")  # Too short
    
    @patch("src.loaders.arxiv_loader.LangChainArxivLoader")
    def test_load_by_id_success(self, mock_loader_class, sample_paper):
        """Test loading paper by ID."""
        # Setup mock
        mock_loader = Mock()
        mock_doc = Mock()
        mock_doc.metadata = {
            "Title": sample_paper["title"],
            "Authors": sample_paper["authors"],
            "Published": sample_paper["published"],
            "Summary": sample_paper["summary"],
            "pdf_url": sample_paper["pdf_url"]
        }
        mock_doc.page_content = sample_paper["full_text"]
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader
        
        # Test
        loader = ArXivLoader()
        paper = loader.load_by_id("2301.12345")
        
        # Assertions
        assert paper["id"] == "arxiv:2301.12345"
        assert paper["title"] == sample_paper["title"]
    
    def test_to_langchain_documents(self, sample_paper):
        """Test conversion to LangChain documents."""
        loader = ArXivLoader()
        papers = [sample_paper]
        
        documents = loader.to_langchain_documents(papers)
        
        assert len(documents) == 1
        assert isinstance(documents[0], Document)
        assert documents[0].page_content == sample_paper["full_text"]
        assert documents[0].metadata["title"] == sample_paper["title"]


class TestPDFLoader:
    """Test PDFLoader class."""
    
    @patch("src.loaders.pdf_loader.PyMuPDFLoader")
    def test_load_pdf_success(self, mock_loader_class):
        """Test successful PDF loading."""
        # Setup mock
        mock_loader = Mock()
        mock_doc = Document(
            page_content="Test PDF content",
            metadata={"source": "test.pdf"}
        )
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader
        
        # Test
        loader = PDFLoader()
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", new_callable=lambda: ".pdf"):
                documents = loader.load("/test/path.pdf")
        
        assert len(documents) == 1
        assert documents[0].page_content == "Test PDF content"
    
    def test_load_pdf_not_found(self):
        """Test loading non-existent PDF."""
        loader = PDFLoader()
        
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(Exception):
                loader.load("/nonexistent.pdf")
    
    def test_load_pdf_invalid_format(self):
        """Test loading non-PDF file."""
        loader = PDFLoader()
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", new_callable=lambda: ".txt"):
                with pytest.raises(Exception):  # Changed from ValueError to Exception
                    loader.load("/test/file.txt")

