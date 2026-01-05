"""General search tool for research papers across multiple sources."""

from typing import Optional, List
from langchain.tools import tool
from pydantic import BaseModel, Field

from src.loaders import ArXivLoader
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SearchPapersInput(BaseModel):
    """Input schema for paper search tool."""
    
    query: str = Field(
        description="Search query for research papers. Can include keywords, topics, or specific paper titles."
    )
    max_results: Optional[int] = Field(
        default=10,
        description="Maximum number of results to return (default: 10)"
    )
    source: Optional[str] = Field(
        default="arxiv",
        description="Source to search (currently supports: 'arxiv')"
    )


@tool(args_schema=SearchPapersInput)
def search_papers_tool(
    query: str,
    max_results: int = 10,
    source: str = "arxiv"
) -> str:
    """
    Search for research papers across multiple sources.
    
    This tool searches for research papers based on the query.
    Currently supports ArXiv, with plans for PubMed and Google Scholar.
    
    Use this tool when:
    - User wants to find research papers
    - User asks about papers on a topic
    - User needs to search academic literature
    
    Args:
        query: Search query (keywords, topics, paper titles)
        max_results: Maximum number of results (default: 10)
        source: Source to search (default: "arxiv")
        
    Returns:
        Formatted string with search results including titles, authors, abstracts, and IDs
        
    Example:
        query="machine learning in healthcare"
        Returns formatted list of papers with full details
    """
    try:
        logger.info(f"Search papers tool called: query='{query}', source={source}, max_results={max_results}")
        
        # Currently only ArXiv supported
        if source.lower() != "arxiv":
            return f"Error: Source '{source}' not yet supported. Currently only 'arxiv' is available."
        
        # Initialize ArXiv loader
        loader = ArXivLoader(max_results=max_results)
        
        # Search papers
        papers = loader.search(query, max_results=max_results)
        
        if not papers:
            return (
                f"No papers found for query: '{query}'\n"
                f"Try:\n"
                f"- Using different keywords\n"
                f"- Broadening your search terms\n"
                f"- Checking spelling"
            )
        
        # Format results with detailed information
        result_lines = [
            f"🔍 Found {len(papers)} papers for '{query}':\n",
            f"Source: {source.upper()}\n",
            "=" * 80 + "\n"
        ]
        
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Unknown Title")
            authors = paper.get("authors", [])
            
            # Format authors
            if isinstance(authors, list):
                if len(authors) <= 3:
                    authors_str = ", ".join(authors)
                else:
                    authors_str = ", ".join(authors[:3]) + f" et al. ({len(authors)} authors)"
            else:
                authors_str = str(authors)
            
            published = paper.get("published", "Unknown Date")
            summary = paper.get("summary", "")
            paper_id = paper.get("id", "")
            pdf_url = paper.get("pdf_url", "")
            
            result_lines.append(
                f"\n📄 Paper {i}:\n"
                f"   Title: {title}\n"
                f"   Authors: {authors_str}\n"
                f"   Published: {published}\n"
                f"   ID: {paper_id}\n"
            )
            
            if pdf_url:
                result_lines.append(f"   PDF: {pdf_url}\n")
            
            if summary:
                # Truncate summary if too long
                summary_display = summary[:300] + "..." if len(summary) > 300 else summary
                result_lines.append(f"   Abstract: {summary_display}\n")
            
            result_lines.append("-" * 80 + "\n")
        
        # Add usage instructions
        result_lines.append(
            f"\n💡 Tip: Use paper IDs to get more details or load specific papers.\n"
            f"   Example: Load paper with ID '{papers[0].get('id', '')}'"
        )
        
        result = "".join(result_lines)
        logger.info(f"Search completed: {len(papers)} papers found")
        return result
        
    except Exception as e:
        logger.error(f"Search papers tool failed: {e}")
        return f"Error searching papers: {str(e)}\nPlease try again with a different query."


class SearchPapersTool:
    """
    Wrapper class for paper search tool.
    
    Provides additional methods and multi-source search capabilities.
    """
    
    def __init__(self, default_max_results: int = 10):
        """
        Initialize search tool.
        
        Args:
            default_max_results: Default maximum results
        """
        self.default_max_results = default_max_results
        self.arxiv_loader = ArXivLoader(max_results=default_max_results)
        logger.info(f"SearchPapersTool initialized: default_max_results={default_max_results}")
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        source: str = "arxiv"
    ) -> List[dict]:
        """
        Search papers and return structured results.
        
        Args:
            query: Search query
            max_results: Maximum results
            source: Source to search
            
        Returns:
            List of paper dictionaries
        """
        try:
            results = max_results or self.default_max_results
            
            if source.lower() == "arxiv":
                papers = self.arxiv_loader.search(query, max_results=results)
            else:
                raise ValueError(f"Unsupported source: {source}")
            
            logger.info(f"Search completed: {len(papers)} papers from {source}")
            return papers
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_multiple_sources(
        self,
        query: str,
        sources: List[str] = None,
        max_results_per_source: int = 5
    ) -> dict:
        """
        Search across multiple sources.
        
        Args:
            query: Search query
            sources: List of sources to search
            max_results_per_source: Results per source
            
        Returns:
            Dictionary with results from each source
        """
        if sources is None:
            sources = ["arxiv"]
        
        results = {}
        
        for source in sources:
            try:
                if source.lower() == "arxiv":
                    papers = self.arxiv_loader.search(query, max_results=max_results_per_source)
                    results[source] = papers
                else:
                    logger.warning(f"Source {source} not yet supported")
                    results[source] = []
            except Exception as e:
                logger.error(f"Failed to search {source}: {e}")
                results[source] = []
        
        logger.info(f"Multi-source search completed: {sum(len(p) for p in results.values())} total papers")
        return results
    
    def get_tool(self):
        """Get LangChain tool instance."""
        return search_papers_tool

