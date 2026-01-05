"""ArXiv search tool for LangChain agents."""

from typing import Optional
from langchain.tools import tool
from pydantic import BaseModel, Field

from src.loaders import ArXivLoader
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ArXivSearchInput(BaseModel):
    """Input schema for ArXiv search tool."""
    
    query: str = Field(
        description="Search query for ArXiv papers. Can be keywords, topics, or paper titles."
    )
    max_results: Optional[int] = Field(
        default=5,
        description="Maximum number of results to return (default: 5)"
    )


@tool(args_schema=ArXivSearchInput)
def arxiv_search_tool(query: str, max_results: int = 5) -> str:
    """
    Search for research papers on ArXiv.
    
    This tool searches ArXiv (arxiv.org) for research papers matching the query.
    It returns paper titles, authors, abstracts, and metadata.
    
    Use this tool when:
    - User asks to find papers on a specific topic
    - User wants to search for research papers
    - User needs information about papers on ArXiv
    
    Args:
        query: Search query (keywords, topics, paper titles)
        max_results: Maximum number of results (default: 5)
        
    Returns:
        Formatted string with search results including titles, authors, and summaries
        
    Example:
        query="transformer models in NLP"
        Returns formatted list of papers with titles, authors, and abstracts
    """
    try:
        logger.info(f"ArXiv search tool called: query='{query}', max_results={max_results}")
        
        # Initialize loader
        loader = ArXivLoader(max_results=max_results)
        
        # Search papers
        papers = loader.search(query, max_results=max_results)
        
        if not papers:
            return f"No papers found for query: '{query}'"
        
        # Format results
        result_lines = [f"Found {len(papers)} papers for '{query}':\n"]
        
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Unknown Title")
            authors = paper.get("authors", [])
            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += f" et al. ({len(authors)} authors)"
            
            published = paper.get("published", "Unknown Date")
            summary = paper.get("summary", "")[:200]  # First 200 chars
            paper_id = paper.get("id", "")
            
            result_lines.append(
                f"\n{i}. {title}\n"
                f"   Authors: {authors_str}\n"
                f"   Published: {published}\n"
                f"   ID: {paper_id}\n"
                f"   Summary: {summary}...\n"
            )
        
        result = "\n".join(result_lines)
        logger.info(f"ArXiv search completed: {len(papers)} papers found")
        return result
        
    except Exception as e:
        logger.error(f"ArXiv search tool failed: {e}")
        return f"Error searching ArXiv: {str(e)}"


class ArXivSearchTool:
    """
    Wrapper class for ArXiv search tool.
    
    Provides additional methods and configuration options.
    """
    
    def __init__(self, max_results: int = 5):
        """
        Initialize ArXiv search tool.
        
        Args:
            max_results: Default maximum results
        """
        self.max_results = max_results
        self.loader = ArXivLoader(max_results=max_results)
        logger.info(f"ArXivSearchTool initialized: max_results={max_results}")
    
    def search(self, query: str, max_results: Optional[int] = None) -> list[dict]:
        """
        Search ArXiv and return structured results.
        
        Args:
            query: Search query
            max_results: Maximum results (overrides default)
            
        Returns:
            List of paper dictionaries
        """
        try:
            results = max_results or self.max_results
            papers = self.loader.search(query, max_results=results)
            logger.info(f"Search completed: {len(papers)} papers")
            return papers
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def load_by_id(self, paper_id: str) -> dict:
        """
        Load a specific paper by ID.
        
        Args:
            paper_id: ArXiv paper ID
            
        Returns:
            Paper dictionary
        """
        try:
            paper = self.loader.load_by_id(paper_id)
            logger.info(f"Loaded paper: {paper.get('title', 'Unknown')[:50]}")
            return paper
        except Exception as e:
            logger.error(f"Failed to load paper {paper_id}: {e}")
            raise
    
    def get_tool(self):
        """Get LangChain tool instance."""
        return arxiv_search_tool

