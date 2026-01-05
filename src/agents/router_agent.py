"""Router agent for directing tasks to appropriate specialized agents."""

from typing import Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger
from src.config import settings
from src.agents import SearchAgent, QAAgent, SummarizationAgent

logger = get_logger(__name__)


class RouterAgent:
    """
    Router agent that directs user queries to appropriate specialized agents.
    
    Capabilities:
    - Analyze user intent
    - Route to search agent (for finding papers)
    - Route to Q&A agent (for answering questions)
    - Route to summarization agent (for summarizing papers)
    - Handle multi-step workflows
    """
    
    def __init__(
        self,
        search_agent: Optional[SearchAgent] = None,
        qa_agent: Optional[QAAgent] = None,
        summarization_agent: Optional[SummarizationAgent] = None,
        llm_model: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize router agent.
        
        Args:
            search_agent: Search agent instance (default: creates new)
            qa_agent: Q&A agent instance (default: creates new)
            summarization_agent: Summarization agent instance (default: creates new)
            llm_model: LLM model name (default: from settings)
            verbose: Enable verbose logging
        """
        self.llm_model = llm_model or settings.llm_model
        self.verbose = verbose
        
        logger.info(f"Initializing RouterAgent: model={self.llm_model}")
        
        # Initialize specialized agents if not provided
        if search_agent is None:
            self.search_agent = SearchAgent(llm_model=self.llm_model, verbose=self.verbose)
        else:
            self.search_agent = search_agent
        
        if qa_agent is None:
            self.qa_agent = QAAgent(llm_model=self.llm_model, verbose=self.verbose)
        else:
            self.qa_agent = qa_agent
        
        if summarization_agent is None:
            self.summarization_agent = SummarizationAgent(
                llm_model=self.llm_model,
                verbose=self.verbose
            )
        else:
            self.summarization_agent = summarization_agent
        
        # Initialize LLM for routing decisions
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0,  # Low temperature for consistent routing
            openai_api_key=settings.openai_api_key,
            request_timeout=settings.request_timeout
        )
        
        # Router doesn't need tools, it routes to other agents
        self.tools = []
        
        # Create router prompt
        router_prompt = """You are a router agent for a research assistant system.

Your job is to analyze user queries and determine which specialized agent should handle them:

1. **Search Agent**: Use when user wants to:
   - Find papers on a topic
   - Search for research papers
   - Discover papers by keywords
   - Examples: "Find papers on transformers", "Search for NLP research"

2. **Q&A Agent**: Use when user wants to:
   - Ask questions about research topics
   - Get explanations about concepts
   - Understand research findings
   - Examples: "What is transformer architecture?", "Explain attention mechanism"

3. **Summarization Agent**: Use when user wants to:
   - Summarize a specific paper
   - Get key points from a paper
   - Understand a paper quickly
   - Examples: "Summarize paper 2301.12345", "Give me key points of this paper"

4. **Multi-step**: Some queries may require multiple agents:
   - First search, then summarize
   - First search, then answer questions
   - Example: "Find papers on transformers and summarize the first one"

Respond with the agent name: "search", "qa", "summarize", or "multi-step" followed by reasoning."""

        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", router_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent (though it won't use tools, just routing logic)
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=self.verbose,
            max_iterations=5,
            max_execution_time=30,
            handle_parsing_errors=True
        )
        
        logger.info("RouterAgent initialized successfully")
    
    def route(self, query: str) -> Dict[str, Any]:
        """
        Route a user query to the appropriate agent.
        
        Args:
            query: User's query
            
        Returns:
            Dictionary with routing decision and result
        """
        try:
            logger.info(f"RouterAgent analyzing query: '{query[:50]}...'")
            
            # Simple keyword-based routing (can be enhanced with LLM)
            query_lower = query.lower()
            
            # Determine intent
            if any(keyword in query_lower for keyword in [
                "summarize", "summary", "key points", "main findings",
                "paper", "arxiv:", "2301", "2302"  # ArXiv ID patterns
            ]):
                intent = "summarize"
            elif any(keyword in query_lower for keyword in [
                "find", "search", "papers on", "research about",
                "discover", "look for"
            ]):
                intent = "search"
            elif any(keyword in query_lower for keyword in [
                "what is", "how does", "explain", "why", "tell me about",
                "question", "?"
            ]):
                intent = "qa"
            else:
                # Default: try Q&A first
                intent = "qa"
            
            logger.info(f"RouterAgent determined intent: {intent}")
            
            # Route to appropriate agent
            if intent == "search":
                result = self.search_agent.search(query)
                return {
                    "intent": "search",
                    "agent": "SearchAgent",
                    "result": result
                }
            
            elif intent == "qa":
                result = self.qa_agent.answer(query)
                return {
                    "intent": "qa",
                    "agent": "QAAgent",
                    "result": result
                }
            
            elif intent == "summarize":
                # Extract paper ID if present
                paper_id = self._extract_paper_id(query)
                if paper_id:
                    result = self.summarization_agent.summarize(paper_id=paper_id)
                else:
                    # Try to search first, then summarize
                    search_result = self.search_agent.search(query)
                    # For now, return search result with note
                    result = {
                        "message": "Please provide a paper ID or specific paper to summarize",
                        "search_results": search_result
                    }
                
                return {
                    "intent": "summarize",
                    "agent": "SummarizationAgent",
                    "result": result
                }
            
            else:
                # Default to Q&A
                result = self.qa_agent.answer(query)
                return {
                    "intent": "qa",
                    "agent": "QAAgent",
                    "result": result
                }
                
        except Exception as e:
            logger.error(f"RouterAgent failed: {e}")
            raise Exception(f"Routing failed: {str(e)}")
    
    def _extract_paper_id(self, query: str) -> Optional[str]:
        """
        Extract ArXiv paper ID from query.
        
        Args:
            query: User query
            
        Returns:
            Paper ID if found, None otherwise
        """
        import re
        
        # Pattern for ArXiv IDs: arxiv:YYMM.NNNNN or YYMM.NNNNN
        patterns = [
            r"arxiv:(\d{4}\.\d{4,5})",
            r"(\d{4}\.\d{4,5})",
            r"paper\s+(\d{4}\.\d{4,5})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def process(self, query: str) -> Dict[str, Any]:
        """
        Process a query by routing to appropriate agent.
        
        This is the main entry point for the router.
        
        Args:
            query: User's query
            
        Returns:
            Complete result with routing information
        """
        return self.route(query)


def create_router_agent(
    search_agent: Optional[SearchAgent] = None,
    qa_agent: Optional[QAAgent] = None,
    summarization_agent: Optional[SummarizationAgent] = None,
    llm_model: Optional[str] = None,
    verbose: bool = False
) -> RouterAgent:
    """
    Factory function to create a router agent.
    
    Args:
        search_agent: Search agent instance
        qa_agent: Q&A agent instance
        summarization_agent: Summarization agent instance
        llm_model: LLM model name
        verbose: Enable verbose logging
        
    Returns:
        RouterAgent instance
    """
    return RouterAgent(
        search_agent=search_agent,
        qa_agent=qa_agent,
        summarization_agent=summarization_agent,
        llm_model=llm_model,
        verbose=verbose
    )

