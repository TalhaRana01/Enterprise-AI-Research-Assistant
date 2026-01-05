"""Paper management endpoints (summarize, cite, etc.)."""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional, List

from src.api.models.schemas import (
    SummarizeRequest,
    SummarizeResponse,
    CitationRequest,
    CitationResponse,
    PaperInfo,
    ErrorResponse
)
from src.agents import SummarizationAgent, create_summarization_agent
from src.chains import CitationChain, create_citation_chain
from src.loaders import ArXivLoader
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/papers", tags=["papers"])

# Initialize agents (singleton pattern)
_summarization_agent: Optional[SummarizationAgent] = None
_citation_chain: Optional[CitationChain] = None


def get_summarization_agent() -> SummarizationAgent:
    """Get or create summarization agent instance."""
    global _summarization_agent
    if _summarization_agent is None:
        _summarization_agent = create_summarization_agent(verbose=False)
    return _summarization_agent


def get_citation_chain() -> CitationChain:
    """Get or create citation chain instance."""
    global _citation_chain
    if _citation_chain is None:
        _citation_chain = create_citation_chain()
    return _citation_chain


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_paper(request: SummarizeRequest):
    """
    Summarize a research paper.
    
    Creates a comprehensive summary of a research paper with key findings,
    methodology, contributions, and limitations.
    
    **Example Request:**
    ```json
    {
        "paper_id": "2301.12345",
        "format": "detailed"
    }
    ```
    
    **Formats:**
    - `detailed`: Full structured summary
    - `short`: Brief summary (200 words)
    - `bullet_points`: Key points as bullets
    """
    try:
        logger.info(f"Summarize request: paper_id={request.paper_id}, format={request.format}")
        
        # Get summarization agent
        agent = get_summarization_agent()
        
        # Summarize based on format
        if request.format == "short":
            if not request.paper_id:
                raise ValueError("paper_id required for short summary")
            
            summary_text = agent.summarize_short(
                paper_id=request.paper_id,
                max_length=request.max_length or 200
            )
            
            # Load paper for metadata
            loader = ArXivLoader()
            paper = loader.load_by_id(request.paper_id)
            
            response = SummarizeResponse(
                summary=summary_text,
                title=paper.get("title", ""),
                authors=paper.get("authors", []),
                published=paper.get("published"),
                paper_id=request.paper_id,
                format="short",
                length=len(summary_text)
            )
            
        elif request.format == "bullet_points":
            if not request.paper_id:
                raise ValueError("paper_id required for bullet points")
            
            points = agent.summarize_bullet_points(
                paper_id=request.paper_id,
                num_points=5
            )
            
            summary_text = "\n".join([f"• {point}" for point in points])
            
            # Load paper for metadata
            loader = ArXivLoader()
            paper = loader.load_by_id(request.paper_id)
            
            response = SummarizeResponse(
                summary=summary_text,
                title=paper.get("title", ""),
                authors=paper.get("authors", []),
                published=paper.get("published"),
                paper_id=request.paper_id,
                format="bullet_points",
                length=len(summary_text)
            )
            
        else:  # detailed
            result = agent.summarize(
                paper_id=request.paper_id,
                title=request.title,
                content=request.content,
                authors=None,
                published=None
            )
            
            response = SummarizeResponse(
                summary=result.get("summary", ""),
                title=result.get("title", ""),
                authors=result.get("authors", []),
                published=result.get("published"),
                paper_id=result.get("paper_id"),
                format="detailed",
                length=result.get("length", 0)
            )
        
        logger.info(f"Summarization completed: format={request.format}, length={response.length}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in summarize: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize paper: {str(e)}"
        )


@router.get("/{paper_id}/summarize", response_model=SummarizeResponse)
async def summarize_paper_by_id(
    paper_id: str = Path(..., description="ArXiv paper ID"),
    format: str = Query(default="detailed", description="Summary format"),
    max_length: int = Query(default=500, ge=50, le=2000, description="Max length for short format")
):
    """
    Summarize a paper by ID (GET endpoint).
    
    **Example:**
    ```
    GET /api/v1/papers/2301.12345/summarize?format=short
    ```
    """
    try:
        request = SummarizeRequest(
            paper_id=paper_id,
            format=format,
            max_length=max_length
        )
        return await summarize_paper(request)
    except Exception as e:
        logger.error(f"GET summarize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cite", response_model=CitationResponse)
async def generate_citation(request: CitationRequest):
    """
    Generate citation in various formats.
    
    **Supported Formats:**
    - `apa`: APA style
    - `mla`: MLA style
    - `chicago`: Chicago style
    - `bibtex`: BibTeX format
    
    **Example Request:**
    ```json
    {
        "title": "Attention Is All You Need",
        "authors": ["Vaswani", "Shazeer", "Parmar"],
        "year": "2017",
        "journal": "NIPS",
        "style": "apa"
    }
    ```
    """
    try:
        logger.info(f"Citation request: style={request.style}")
        
        # Get citation chain
        chain = get_citation_chain()
        
        # Generate citation
        citation = chain.generate(
            title=request.title,
            authors=request.authors,
            year=request.year,
            journal=request.journal,
            doi=request.doi,
            url=request.url,
            style=request.style
        )
        
        response = CitationResponse(
            citation=citation,
            style=request.style
        )
        
        logger.info(f"Citation generated: style={request.style}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in citation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Citation generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate citation: {str(e)}"
        )


@router.get("/{paper_id}", response_model=PaperInfo)
async def get_paper_info(
    paper_id: str = Path(..., description="ArXiv paper ID")
):
    """
    Get paper information by ID.
    
    **Example:**
    ```
    GET /api/v1/papers/2301.12345
    ```
    """
    try:
        logger.info(f"Get paper info: paper_id={paper_id}")
        
        loader = ArXivLoader()
        paper = loader.load_by_id(paper_id)
        
        paper_info = PaperInfo(
            id=paper.get("id", ""),
            title=paper.get("title", ""),
            authors=paper.get("authors", []),
            published=paper.get("published"),
            summary=paper.get("summary"),
            pdf_url=paper.get("pdf_url"),
            source=paper.get("source", "arxiv")
        )
        
        return paper_info
        
    except ValueError as e:
        logger.error(f"Paper not found: {e}")
        raise HTTPException(status_code=404, detail=f"Paper not found: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))

