"""Search agent for finding research papers."""

from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger
from src.config import settings
from src.prompts import load_prompt
from src.tools import search_papers_tool, arxiv_search_tool

logger = get_logger(__name__)


class SearchAgent:
    """
    Agent specialized in searching for research papers.
    
    Capabilities:
    - Search papers across multiple sources
    - Filter and rank results
    - Provide detailed paper information
    - Handle complex search queries
    """
    
    def __init__(
        self,
        llm_model: Optional[str] = None,
        tools: Optional[List] = None,
        verbose: bool = False
    ):
        """
        Initialize search agent.
        
        Args:
            llm_model: LLM model name (default: from settings)
            tools: List of tools (default: search tools)
            verbose: Enable verbose logging
        """
        self.llm_model = llm_model or settings.llm_model
        self.verbose = verbose
        
        logger.info(f"Initializing SearchAgent: model={self.llm_model}")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0,  # Low temperature for consistent search
            openai_api_key=settings.openai_api_key,
            request_timeout=settings.request_timeout
        )
        
        # Setup tools
        if tools is None:
            self.tools = [search_papers_tool, arxiv_search_tool]
        else:
            self.tools = tools
        
        # Load search prompt
        try:
            system_prompt = load_prompt("search_prompt")
        except Exception as e:
            logger.warning(f"Failed to load search_prompt, using default: {e}")
            system_prompt = """You are a specialized research paper search agent. 
Your task is to help users find relevant research papers based on their queries.

When searching:
1. Understand the user's research question or topic
2. Identify key terms and concepts
3. Search across multiple sources
4. Rank results by relevance
5. Provide concise summaries of each paper

Always prioritize:
- Recent papers (when recency matters)
- Highly cited papers (when quality matters)
- Papers from reputable sources

Format your response clearly with numbered results and brief explanations."""
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
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
            max_iterations=10,
            max_execution_time=60,
            handle_parsing_errors=True,
            return_intermediate_steps=self.verbose
        )
        
        logger.info("SearchAgent initialized successfully")
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Search for research papers.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            logger.info(f"SearchAgent processing query: '{query[:50]}...'")
            
            # Invoke agent
            result = self.agent_executor.invoke({"input": query})
            
            logger.info("SearchAgent completed successfully")
            return {
                "output": result.get("output", ""),
                "query": query,
                "intermediate_steps": result.get("intermediate_steps", []) if self.verbose else []
            }
            
        except Exception as e:
            logger.error(f"SearchAgent failed: {e}")
            raise Exception(f"Search failed: {str(e)}")
    
    def search_with_context(
        self,
        query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search with additional context.
        
        Args:
            query: Search query
            context: Additional context about what user is looking for
            
        Returns:
            Search results with context
        """
        try:
            # Enhance query with context
            enhanced_query = query
            if context:
                enhanced_query = f"{query}\n\nContext: {context}"
            
            return self.search(enhanced_query)
            
        except Exception as e:
            logger.error(f"Contextual search failed: {e}")
            raise


def create_search_agent(
    llm_model: Optional[str] = None,
    tools: Optional[List] = None,
    verbose: bool = False
) -> SearchAgent:
    """
    Factory function to create a search agent.
    
    Args:
        llm_model: LLM model name
        tools: List of tools
        verbose: Enable verbose logging
        
    Returns:
        SearchAgent instance
    """
    return SearchAgent(
        llm_model=llm_model,
        tools=tools,
        verbose=verbose
    )

