"""Pydantic schemas for API request and response models."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PaperInfo(BaseModel):
    """Paper information schema."""
    
    id: str = Field(..., description="Paper ID (e.g., arxiv:2301.12345)")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    published: Optional[str] = Field(None, description="Publication date")
    summary: Optional[str] = Field(None, description="Paper summary/abstract")
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    source: str = Field(default="arxiv", description="Source (arxiv, pubmed, etc.)")


class SearchRequest(BaseModel):
    """Request schema for paper search."""
    
    query: str = Field(..., min_length=3, description="Search query string")
    max_results: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results (1-50)"
    )
    source: Optional[str] = Field(
        default="arxiv",
        description="Source to search (arxiv, pubmed, etc.)"
    )


class SearchResponse(BaseModel):
    """Response schema for paper search."""
    
    query: str = Field(..., description="Original search query")
    papers: List[PaperInfo] = Field(default_factory=list, description="List of papers")
    total: int = Field(..., description="Total number of results")
    source: str = Field(..., description="Source used for search")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ChatRequest(BaseModel):
    """Request schema for Q&A chat."""
    
    question: str = Field(..., min_length=1, description="User's question")
    paper_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific paper IDs to use for context"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation continuity"
    )


class ChatResponse(BaseModel):
    """Response schema for Q&A chat."""
    
    answer: str = Field(..., description="Generated answer")
    question: str = Field(..., description="Original question")
    sources: List[PaperInfo] = Field(
        default_factory=list,
        description="Papers used as sources"
    )
    num_sources: int = Field(default=0, description="Number of sources used")
    session_id: Optional[str] = Field(None, description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class SummarizeRequest(BaseModel):
    """Request schema for paper summarization."""
    
    paper_id: Optional[str] = Field(
        None,
        description="ArXiv paper ID (e.g., 2301.12345 or arxiv:2301.12345)"
    )
    title: Optional[str] = Field(None, description="Paper title (if paper_id not provided)")
    content: Optional[str] = Field(None, description="Paper content (if paper_id not provided)")
    format: Optional[str] = Field(
        default="detailed",
        description="Summary format: detailed, short, or bullet_points"
    )
    max_length: Optional[int] = Field(
        default=500,
        ge=50,
        le=2000,
        description="Maximum length for short summary"
    )


class SummarizeResponse(BaseModel):
    """Response schema for paper summarization."""
    
    summary: str = Field(..., description="Generated summary")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="Authors")
    published: Optional[str] = Field(None, description="Publication date")
    paper_id: Optional[str] = Field(None, description="Paper ID")
    format: str = Field(..., description="Summary format used")
    length: int = Field(..., description="Summary length in characters")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class CitationRequest(BaseModel):
    """Request schema for citation generation."""
    
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of authors")
    year: str = Field(..., description="Publication year")
    journal: Optional[str] = Field(None, description="Journal/conference name")
    doi: Optional[str] = Field(None, description="DOI")
    url: Optional[str] = Field(None, description="URL")
    style: str = Field(
        default="apa",
        description="Citation style: apa, mla, chicago, or bibtex"
    )


class CitationResponse(BaseModel):
    """Response schema for citation generation."""
    
    citation: str = Field(..., description="Formatted citation")
    style: str = Field(..., description="Citation style used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")

