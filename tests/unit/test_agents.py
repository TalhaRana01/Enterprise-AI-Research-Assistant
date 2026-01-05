"""Unit tests for agents."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents import SearchAgent, QAAgent, SummarizationAgent, RouterAgent


class TestSearchAgent:
    """Test Search Agent."""
    
    @patch("src.agents.search_agent.ChatOpenAI")
    def test_search_agent_init(self, mock_llm_class):
        """Test search agent initialization."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        with patch("src.agents.search_agent.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            agent = SearchAgent()
            
            assert agent is not None
            assert agent.tools is not None
    
    @patch("src.agents.search_agent.ChatOpenAI")
    def test_search_method(self, mock_llm_class):
        """Test search method."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        with patch("src.agents.search_agent.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            agent = SearchAgent()
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.return_value = {
                "output": "Found papers on transformers"
            }
            
            result = agent.search("transformer models")
            
            assert "output" in result
            agent.agent_executor.invoke.assert_called_once()


class TestQAAgent:
    """Test Q&A Agent."""
    
    @patch("src.agents.qa_agent.create_rag_chain")
    @patch("src.agents.qa_agent.ChatOpenAI")
    def test_qa_agent_init(self, mock_llm_class, mock_rag_chain):
        """Test Q&A agent initialization."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        mock_rag = Mock()
        mock_rag_chain.return_value = mock_rag
        
        with patch("src.agents.qa_agent.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.llm_temperature = 0
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            agent = QAAgent()
            
            assert agent is not None
            assert agent.rag_chain is not None
    
    @patch("src.agents.qa_agent.create_rag_chain")
    @patch("src.agents.qa_agent.ChatOpenAI")
    def test_answer_method(self, mock_llm_class, mock_rag_chain):
        """Test answer method."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        mock_rag = Mock()
        mock_rag.invoke.return_value = {
            "answer": "Test answer",
            "sources": [],
            "num_sources": 0
        }
        mock_rag_chain.return_value = mock_rag
        
        with patch("src.agents.qa_agent.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.llm_temperature = 0
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            agent = QAAgent()
            
            result = agent.answer("What is AI?")
            
            assert "answer" in result
            assert result["answer"] == "Test answer"


class TestRouterAgent:
    """Test Router Agent."""
    
    @patch("src.agents.router_agent.SearchAgent")
    @patch("src.agents.router_agent.QAAgent")
    @patch("src.agents.router_agent.SummarizationAgent")
    @patch("src.agents.router_agent.ChatOpenAI")
    def test_router_agent_init(
        self,
        mock_llm_class,
        mock_summarization_agent_class,
        mock_qa_agent_class,
        mock_search_agent_class
    ):
        """Test router agent initialization."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        mock_search = Mock()
        mock_qa = Mock()
        mock_summarization = Mock()
        
        mock_search_agent_class.return_value = mock_search
        mock_qa_agent_class.return_value = mock_qa
        mock_summarization_agent_class.return_value = mock_summarization
        
        with patch("src.agents.router_agent.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            router = RouterAgent()
            
            assert router is not None
            assert router.search_agent is not None
            assert router.qa_agent is not None
            assert router.summarization_agent is not None
    
    @patch("src.agents.router_agent.SearchAgent")
    @patch("src.agents.router_agent.QAAgent")
    @patch("src.agents.router_agent.SummarizationAgent")
    @patch("src.agents.router_agent.ChatOpenAI")
    def test_route_search_intent(
        self,
        mock_llm_class,
        mock_summarization_agent_class,
        mock_qa_agent_class,
        mock_search_agent_class
    ):
        """Test routing to search agent."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        mock_search = Mock()
        mock_search.search.return_value = {"output": "Found papers"}
        mock_search_agent_class.return_value = mock_search
        
        mock_qa = Mock()
        mock_summarization = Mock()
        mock_qa_agent_class.return_value = mock_qa
        mock_summarization_agent_class.return_value = mock_summarization
        
        with patch("src.agents.router_agent.settings") as mock_settings:
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.openai_api_key = "test-key"
            mock_settings.request_timeout = 30
            
            router = RouterAgent()
            
            result = router.route("find papers on transformers")
            
            assert result["intent"] == "search"
            assert result["agent"] == "SearchAgent"
            mock_search.search.assert_called_once()

