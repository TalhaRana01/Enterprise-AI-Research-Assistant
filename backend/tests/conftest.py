"""Pytest configuration and shared fixtures."""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["VECTOR_DB_TYPE"] = "chroma"
os.environ["CHROMA_PERSIST_DIRECTORY"] = "./tests/data/chroma_test"


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import patch
    with patch("src.config.settings") as mock:
        mock.environment = "test"
        mock.openai_api_key = "test-key"
        mock.llm_model = "gpt-3.5-turbo"
        mock.vector_db_type = "chroma"
        mock.chroma_persist_directory = "./tests/data/chroma_test"
        yield mock


@pytest.fixture
def sample_paper():
    """Sample paper data for testing."""
    return {
        "id": "arxiv:2301.12345",
        "title": "Test Paper: Transformer Architecture",
        "authors": ["John Doe", "Jane Smith"],
        "published": "2023-01-01",
        "summary": "This is a test paper about transformer architecture.",
        "full_text": "Full text content of the test paper...",
        "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
        "source": "arxiv"
    }


@pytest.fixture
def sample_documents():
    """Sample LangChain Document objects for testing."""
    from langchain_core.documents import Document
    
    return [
        Document(
            page_content="This is test content about transformers.",
            metadata={
                "id": "arxiv:2301.12345",
                "title": "Test Paper",
                "authors": "John Doe",
                "source": "arxiv"
            }
        ),
        Document(
            page_content="This is another test content about NLP.",
            metadata={
                "id": "arxiv:2302.67890",
                "title": "Another Test Paper",
                "authors": "Jane Smith",
                "source": "arxiv"
            }
        )
    ]


@pytest.fixture
def mock_arxiv_loader():
    """Mock ArXivLoader for testing."""
    from unittest.mock import Mock
    loader = Mock()
    loader.search.return_value = [
        {
            "id": "arxiv:2301.12345",
            "title": "Test Paper",
            "authors": ["John Doe"],
            "published": "2023-01-01",
            "summary": "Test summary",
            "full_text": "Test content",
            "source": "arxiv"
        }
    ]
    loader.load_by_id.return_value = {
        "id": "arxiv:2301.12345",
        "title": "Test Paper",
        "authors": ["John Doe"],
        "published": "2023-01-01",
        "summary": "Test summary",
        "full_text": "Test content",
        "source": "arxiv"
    }
    return loader


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    from unittest.mock import Mock
    llm = Mock()
    llm.invoke.return_value = Mock(content="Test response")
    return llm

