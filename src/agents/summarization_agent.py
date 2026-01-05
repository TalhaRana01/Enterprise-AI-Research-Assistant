"""Summarization agent for creating summaries of research papers."""

from typing import Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger
from src.config import settings
from src.prompts import load_prompt
from src.chains import SummarizationChain, create_summarization_chain
from src.loaders import ArXivLoader
from src.tools import arxiv_search_tool

logger = get_logger(__name__)


class SummarizationAgent:
    """
    Agent specialized in summarizing research papers.
    
    Capabilities:
    - Summarize papers from ArXiv IDs
    - Create detailed structured summaries
    - Generate short summaries or bullet points
    - Extract key findings and methodologies
    """
    
    def __init__(
        self,
        summarization_chain: Optional[SummarizationChain] = None,
        llm_model: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize summarization agent.
        
        Args:
            summarization_chain: Summarization chain instance (default: creates new)
            llm_model: LLM model name (default: from settings)
            verbose: Enable verbose logging
        """
        self.llm_model = llm_model or settings.llm_model
        self.verbose = verbose
        
        logger.info(f"Initializing SummarizationAgent: model={self.llm_model}")
        
        # Initialize summarization chain if not provided
        if summarization_chain is None:
            self.summarization_chain = create_summarization_chain(llm_model=self.llm_model)
        else:
            self.summarization_chain = summarization_chain
        
        # Initialize LLM for agent reasoning
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key,
            request_timeout=settings.request_timeout
        )
        
        # Setup tools
        self.tools = [arxiv_search_tool]
        
        # Initialize loader for fetching papers
        self.loader = ArXivLoader()
        
        # Load system prompt
        try:
            system_prompt = load_prompt("system_prompt")
        except Exception as e:
            logger.warning(f"Failed to load system_prompt, using default: {e}")
            system_prompt = """You are a specialized research paper summarization agent.

Your task is to help users understand research papers by creating comprehensive summaries.

When summarizing:
1. Extract key findings and contributions
2. Explain methodologies used
3. Highlight important results
4. Note limitations if mentioned
5. Provide clear, structured summaries

You can:
- Summarize papers by ArXiv ID
- Create detailed or short summaries
- Generate bullet point summaries
- Extract specific information from papers"""
        
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
            max_execution_time=90,
            handle_parsing_errors=True,
            return_intermediate_steps=self.verbose
        )
        
        logger.info("SummarizationAgent initialized successfully")
    
    def summarize(
        self,
        paper_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        authors: Optional[list] = None,
        published: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize a research paper.
        
        Args:
            paper_id: ArXiv paper ID (e.g., "2301.12345")
            title: Paper title (if paper_id not provided)
            content: Paper content (if paper_id not provided)
            authors: List of authors (optional)
            published: Publication date (optional)
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            # If paper_id provided, load paper first
            if paper_id:
                logger.info(f"Loading paper for summarization: {paper_id}")
                paper = self.loader.load_by_id(paper_id)
                
                title = paper.get("title", "")
                content = paper.get("full_text", paper.get("summary", ""))
                authors = paper.get("authors", [])
                published = paper.get("published", "")
            
            if not title or not content:
                raise ValueError("Either paper_id or (title and content) must be provided")
            
            logger.info(f"Summarizing paper: {title[:50]}...")
            
            # Use summarization chain
            result = self.summarization_chain.summarize(
                title=title,
                content=content,
                authors=authors,
                published=published
            )
            
            # Add paper ID if available
            if paper_id:
                result["paper_id"] = paper_id
            
            logger.info("Summarization completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise Exception(f"Failed to summarize paper: {str(e)}")
    
    def summarize_short(
        self,
        paper_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        max_length: int = 200
    ) -> str:
        """
        Generate a short summary (abstract-like).
        
        Args:
            paper_id: ArXiv paper ID
            title: Paper title
            content: Paper content
            max_length: Maximum summary length
            
        Returns:
            Short summary string
        """
        try:
            # Load paper if ID provided
            if paper_id:
                paper = self.loader.load_by_id(paper_id)
                title = paper.get("title", "")
                content = paper.get("full_text", paper.get("summary", ""))
            
            if not title or not content:
                raise ValueError("Either paper_id or (title and content) must be provided")
            
            logger.info(f"Generating short summary for: {title[:50]}...")
            
            summary = self.summarization_chain.summarize_short(
                title=title,
                content=content,
                max_length=max_length
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Short summarization failed: {e}")
            raise Exception(f"Failed to generate short summary: {str(e)}")
    
    def summarize_bullet_points(
        self,
        paper_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        num_points: int = 5
    ) -> list[str]:
        """
        Generate summary as bullet points.
        
        Args:
            paper_id: ArXiv paper ID
            title: Paper title
            content: Paper content
            num_points: Number of bullet points
            
        Returns:
            List of bullet point strings
        """
        try:
            # Load paper if ID provided
            if paper_id:
                paper = self.loader.load_by_id(paper_id)
                title = paper.get("title", "")
                content = paper.get("full_text", paper.get("summary", ""))
            
            if not title or not content:
                raise ValueError("Either paper_id or (title and content) must be provided")
            
            logger.info(f"Generating bullet points for: {title[:50]}...")
            
            points = self.summarization_chain.summarize_bullet_points(
                title=title,
                content=content,
                num_points=num_points
            )
            
            return points
            
        except Exception as e:
            logger.error(f"Bullet point summarization failed: {e}")
            raise Exception(f"Failed to generate bullet points: {str(e)}")
    
    def summarize_multiple(
        self,
        paper_ids: list[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Summarize multiple papers.
        
        Args:
            paper_ids: List of ArXiv paper IDs
            
        Returns:
            Dictionary mapping paper_id to summary
        """
        try:
            logger.info(f"Summarizing {len(paper_ids)} papers")
            
            summaries = {}
            for paper_id in paper_ids:
                try:
                    summary = self.summarize(paper_id=paper_id)
                    summaries[paper_id] = summary
                except Exception as e:
                    logger.warning(f"Failed to summarize {paper_id}: {e}")
                    summaries[paper_id] = {"error": str(e)}
            
            logger.info(f"Completed summarization of {len(summaries)} papers")
            return summaries
            
        except Exception as e:
            logger.error(f"Multiple summarization failed: {e}")
            raise Exception(f"Failed to summarize multiple papers: {str(e)}")


def create_summarization_agent(
    summarization_chain: Optional[SummarizationChain] = None,
    llm_model: Optional[str] = None,
    verbose: bool = False
) -> SummarizationAgent:
    """
    Factory function to create a summarization agent.
    
    Args:
        summarization_chain: Summarization chain instance
        llm_model: LLM model name
        verbose: Enable verbose logging
        
    Returns:
        SummarizationAgent instance
    """
    return SummarizationAgent(
        summarization_chain=summarization_chain,
        llm_model=llm_model,
        verbose=verbose
    )

