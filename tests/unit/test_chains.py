"""Unit tests for chains."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

from src.chains import VectorStore, RAGChain, CitationChain, SummarizationChain


class TestVectorStore:
    """Test VectorStore class."""
    
    @patch("src.chains.vector_store.Chroma")
    def test_init_chroma(self, mock_chroma_class):
        """Test Chroma initialization."""
        with patch("src.chains.vector_store.settings") as mock_settings:
            mock_settings.vector_db_type = "chroma"
            mock_settings.chroma_persist_directory = "./test_data"
            mock_settings.embedding_model = "text-embedding-3-small"
            mock_settings.openai_api_key = "test-key"
            
            mock_chroma = Mock()
            mock_chroma_class.return_value = mock_chroma
            
            vector_store = VectorStore()
            
            assert vector_store.vector_db_type == "chroma"
            mock_chroma_class.assert_called_once()
    
    def test_add_documents(self):
        """Test adding documents to vector store."""
        with patch("src.chains.vector_store.Chroma") as mock_chroma_class:
            with patch("src.chains.vector_store.settings") as mock_settings:
                mock_settings.vector_db_type = "chroma"
                mock_settings.chroma_persist_directory = "./test_data"
                mock_settings.embedding_model = "text-embedding-3-small"
                mock_settings.openai_api_key = "test-key"
                
                mock_chroma = Mock()
                mock_chroma.add_documents.return_value = ["doc1", "doc2"]
                mock_chroma_class.return_value = mock_chroma
                
                vector_store = VectorStore()
                docs = [
                    Document(page_content="Test", metadata={"id": "1"}),
                    Document(page_content="Test2", metadata={"id": "2"})
                ]
                
                result = vector_store.add_documents(docs)
                
                assert len(result) == 2
                mock_chroma.add_documents.assert_called_once()
    
    def test_similarity_search(self):
        """Test similarity search."""
        with patch("src.chains.vector_store.Chroma") as mock_chroma_class:
            with patch("src.chains.vector_store.settings") as mock_settings:
                mock_settings.vector_db_type = "chroma"
                mock_settings.chroma_persist_directory = "./test_data"
                mock_settings.embedding_model = "text-embedding-3-small"
                mock_settings.openai_api_key = "test-key"
                
                mock_chroma = Mock()
                mock_doc = Document(page_content="Test", metadata={"id": "1"})
                mock_chroma.similarity_search.return_value = [mock_doc]
                mock_chroma_class.return_value = mock_chroma
                
                vector_store = VectorStore()
                results = vector_store.similarity_search("test query", k=5)
                
                assert len(results) == 1
                mock_chroma.similarity_search.assert_called_once()


class TestRAGChain:
    """Test RAG Chain."""
    
    @patch("src.chains.rag_chain.get_vector_store")
    @patch("src.chains.rag_chain.ChatOpenAI")
    def test_rag_chain_init(self, mock_llm_class, mock_vector_store):
        """Test RAG chain initialization."""
        # Setup mocks
        mock_vector_store_instance = Mock()
        mock_retriever = Mock()
        mock_vector_store_instance.as_retriever.return_value = mock_retriever
        mock_vector_store.return_value = mock_vector_store_instance
        
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        with patch("src.chains.rag_chain.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.llm_temperature = 0
            mock_settings.llm_max_tokens = 2000
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            rag_chain = RAGChain()
            
            assert rag_chain is not None
            mock_vector_store_instance.as_retriever.assert_called_once()


class TestCitationChain:
    """Test Citation Chain."""
    
    @patch("src.chains.citation_chain.ChatOpenAI")
    def test_citation_chain_init(self, mock_llm_class):
        """Test citation chain initialization."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        with patch("src.chains.citation_chain.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.openai_api_key = "test-key"
            
            citation_chain = CitationChain()
            
            assert citation_chain is not None
    
    @patch("src.chains.citation_chain.ChatOpenAI")
    def test_generate_apa_citation(self, mock_llm_class):
        """Test APA citation generation."""
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "Doe, J. (2023). Test Paper. Journal Name."
        mock_llm_class.return_value = mock_llm
        
        with patch("src.chains.citation_chain.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.openai_api_key = "test-key"
            
            citation_chain = CitationChain()
            citation_chain.chain = mock_chain
            
            result = citation_chain.generate_apa(
                title="Test Paper",
                authors=["John Doe"],
                year="2023",
                journal="Journal Name"
            )
            
            assert "Doe" in result
            assert "2023" in result


class TestSummarizationChain:
    """Test Summarization Chain."""
    
    @patch("src.chains.summarization_chain.ChatOpenAI")
    def test_summarization_chain_init(self, mock_llm_class):
        """Test summarization chain initialization."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        with patch("src.chains.summarization_chain.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.llm_temperature = 0
            mock_settings.llm_max_tokens = 2000
            mock_settings.openai_api_key = "test-key"
            
            summarization_chain = SummarizationChain()
            
            assert summarization_chain is not None

