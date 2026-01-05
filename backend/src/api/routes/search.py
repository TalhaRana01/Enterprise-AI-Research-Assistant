"""Search endpoints for finding research papers."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.api.models.schemas import SearchRequest, SearchResponse, PaperInfo, ErrorResponse
from src.agents import SearchAgent, create_search_agent
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["search"])

# Initialize search agent (singleton pattern)
_search_agent: Optional[SearchAgent] = None


def get_search_agent() -> SearchAgent:
    """Get or create search agent instance."""
    global _search_agent
    if _search_agent is None:
        _search_agent = create_search_agent(verbose=False)
    return _search_agent


@router.post("", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """
    Search for research papers.
    
    This endpoint searches for research papers across multiple sources
    based on the provided query.
    
    **Example Request:**
    ```json
    {
        "query": "transformer models in NLP",
        "max_results": 10,
        "source": "arxiv"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "query": "transformer models in NLP",
        "papers": [
            {
                "id": "arxiv:2301.12345",
                "title": "Paper Title",
                "authors": ["Author1", "Author2"],
                "published": "2023-01-01",
                "summary": "Paper abstract...",
                "source": "arxiv"
            }
        ],
        "total": 10,
        "source": "arxiv"
    }
    ```
    """
    try:
        logger.info(f"Search request: query='{request.query}', max_results={request.max_results}")
        
        # Get search agent
        agent = get_search_agent()
        
        # Perform search
        result = agent.search(request.query)
        
        # Parse results (agent returns formatted string, need to extract papers)
        # For now, use search tool directly
        from src.tools import search_papers_tool
        
        search_result = search_papers_tool.invoke({
            "query": request.query,
            "max_results": request.max_results,
            "source": request.source
        })
        
        # Use ArXivLoader for structured results
        from src.loaders import ArXivLoader
        loader = ArXivLoader(max_results=request.max_results)
        papers_data = loader.search(request.query, max_results=request.max_results)
        
        # Convert to PaperInfo objects
        papers = [
            PaperInfo(
                id=paper.get("id", ""),
                title=paper.get("title", ""),
                authors=paper.get("authors", []),
                published=paper.get("published"),
                summary=paper.get("summary"),
                pdf_url=paper.get("pdf_url"),
                source=paper.get("source", "arxiv")
            )
            for paper in papers_data
        ]
        
        response = SearchResponse(
            query=request.query,
            papers=papers,
            total=len(papers),
            source=request.source or "arxiv"
        )
        
        logger.info(f"Search completed: {len(papers)} papers found")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in search: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("", response_model=SearchResponse)
async def search_papers_get(
    query: str = Query(..., min_length=3, description="Search query"),
    max_results: int = Query(default=10, ge=1, le=50, description="Maximum results"),
    source: str = Query(default="arxiv", description="Source to search")
):
    """
    Search for research papers (GET endpoint).
    
    Same functionality as POST endpoint but using query parameters.
    
    **Example:**
    ```
    GET /api/v1/search?query=transformer+models&max_results=10
    ```
    """
    try:
        # Convert GET params to SearchRequest
        request = SearchRequest(
            query=query,
            max_results=max_results,
            source=source
        )
        
        # Use POST endpoint logic
        return await search_papers(request)
        
    except Exception as e:
        logger.error(f"GET search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

