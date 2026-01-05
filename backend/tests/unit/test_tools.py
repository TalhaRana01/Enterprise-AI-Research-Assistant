"""Unit tests for tools."""

import pytest
from unittest.mock import Mock, patch

from src.tools import arxiv_search_tool, pdf_process_tool, search_papers_tool


class TestArXivSearchTool:
    """Test ArXiv search tool."""
    
    @patch("src.tools.arxiv_tool.ArXivLoader")
    def test_arxiv_search_tool_success(self, mock_loader_class):
        """Test successful ArXiv search."""
        # Setup mock
        mock_loader = Mock()
        mock_loader.search.return_value = [
            {
                "id": "arxiv:2301.12345",
                "title": "Test Paper",
                "authors": ["John Doe"],
                "published": "2023-01-01",
                "summary": "Test summary",
                "source": "arxiv"
            }
        ]
        mock_loader_class.return_value = mock_loader
        
        # Test
        result = arxiv_search_tool.invoke({
            "query": "transformer models",
            "max_results": 5
        })
        
        # Assertions
        assert "Found 1 papers" in result
        assert "Test Paper" in result
        mock_loader.search.assert_called_once()
    
    @patch("src.tools.arxiv_tool.ArXivLoader")
    def test_arxiv_search_tool_no_results(self, mock_loader_class):
        """Test search with no results."""
        # Setup mock
        mock_loader = Mock()
        mock_loader.search.return_value = []
        mock_loader_class.return_value = mock_loader
        
        # Test
        result = arxiv_search_tool.invoke({
            "query": "nonexistent topic",
            "max_results": 5
        })
        
        # Assertions
        assert "No papers found" in result


class TestSearchPapersTool:
    """Test search papers tool."""
    
    @patch("src.tools.search_tool.ArXivLoader")
    def test_search_papers_tool_success(self, mock_loader_class):
        """Test successful paper search."""
        # Setup mock
        mock_loader = Mock()
        mock_loader.search.return_value = [
            {
                "id": "arxiv:2301.12345",
                "title": "Test Paper",
                "authors": ["John Doe"],
                "published": "2023-01-01",
                "summary": "Test summary",
                "source": "arxiv"
            }
        ]
        mock_loader_class.return_value = mock_loader
        
        # Test
        result = search_papers_tool.invoke({
            "query": "transformer models",
            "max_results": 10,
            "source": "arxiv"
        })
        
        # Assertions
        assert "Found 1 papers" in result
        assert "Test Paper" in result
    
    def test_search_papers_tool_unsupported_source(self):
        """Test search with unsupported source."""
        result = search_papers_tool.invoke({
            "query": "test",
            "source": "pubmed"  # Not yet supported
        })
        
        assert "not yet supported" in result.lower()


class TestPDFProcessTool:
    """Test PDF processing tool."""
    
    @patch("src.tools.pdf_tool.PDFLoader")
    def test_pdf_process_tool_success(self, mock_loader_class):
        """Test successful PDF processing."""
        # Setup mock
        mock_loader = Mock()
        from langchain_core.documents import Document
        mock_doc = Document(
            page_content="Test PDF content",
            metadata={"file_name": "test.pdf"}
        )
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader
        
        # Test
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", new_callable=lambda: ".pdf"):
                result = pdf_process_tool.invoke({
                    "file_path": "/test/path.pdf",
                    "extract_text": True
                })
        
        # Assertions
        assert "Extracted 1 pages" in result
        assert "Test PDF content" in result
    
    def test_pdf_process_tool_file_not_found(self):
        """Test PDF processing with non-existent file."""
        with patch("pathlib.Path.exists", return_value=False):
            result = pdf_process_tool.invoke({
                "file_path": "/nonexistent.pdf",
                "extract_text": True
            })
        
        assert "not found" in result.lower()

