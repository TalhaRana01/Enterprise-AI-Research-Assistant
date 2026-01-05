"""ArXiv paper loader for fetching and processing research papers."""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import ArxivLoader as LangChainArxivLoader

from src.utils.logger import get_logger
from src.utils.validators import validate_paper_id
from src.config import settings

logger = get_logger(__name__)


class ArXivLoader:
    """
    Load research papers from ArXiv.
    
    Supports:
    - Searching papers by query
    - Loading specific papers by ID
    - Extracting metadata (title, authors, abstract, etc.)
    """
    
    def __init__(self, max_results: Optional[int] = None):
        """
        Initialize ArXiv loader.
        
        Args:
            max_results: Maximum number of results to return (default from settings)
        """
        self.max_results = max_results or settings.arxiv_max_results
        logger.info(f"ArXivLoader initialized with max_results={self.max_results}")
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search papers on ArXiv.
        
        Args:
            query: Search query string
            max_results: Maximum results to return
            sort_by: Sort order ("relevance", "lastUpdatedDate", "submittedDate")
            
        Returns:
            List of paper dictionaries with metadata
            
        Raises:
            ValueError: If query is invalid
            Exception: If ArXiv API call fails
        """
        try:
            if not query or len(query.strip()) < 3:
                raise ValueError("Query must be at least 3 characters")
            
            logger.info(f"Searching ArXiv: '{query}'")
            
            # Use LangChain's ArXiv loader
            loader = LangChainArxivLoader(
                query=query,
                load_max_docs=max_results or self.max_results
            )
            
            # Load documents
            documents = loader.load()
            
            # Convert to dictionaries with metadata
            papers = []
            for doc in documents:
                paper = {
                    "id": doc.metadata.get("Entry ID", ""),
                    "title": doc.metadata.get("Title", ""),
                    "authors": doc.metadata.get("Authors", []),
                    "published": doc.metadata.get("Published", ""),
                    "summary": doc.page_content[:500],  # First 500 chars
                    "full_text": doc.page_content,
                    "pdf_url": doc.metadata.get("pdf_url", ""),
                    "source": "arxiv"
                }
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers for query: '{query}'")
            return papers
            
        except Exception as e:
            logger.error(f"ArXiv search failed: {e}")
            raise Exception(f"Failed to search ArXiv: {str(e)}")
    
    def load_by_id(self, paper_id: str) -> Dict[str, Any]:
        """
        Load a specific paper by ArXiv ID.
        
        Args:
            paper_id: ArXiv paper ID (e.g., "2301.12345" or "arxiv:2301.12345")
            
        Returns:
            Paper dictionary with full content
            
        Raises:
            ValueError: If paper_id format is invalid
            Exception: If paper not found or API fails
        """
        try:
            # Clean paper ID
            if paper_id.startswith("arxiv:"):
                paper_id = paper_id.replace("arxiv:", "")
            
            if not validate_paper_id(f"arxiv:{paper_id}"):
                raise ValueError(f"Invalid ArXiv paper ID format: {paper_id}")
            
            logger.info(f"Loading ArXiv paper: {paper_id}")
            
            # Use LangChain loader
            loader = LangChainArxivLoader(query=f"id:{paper_id}")
            documents = loader.load()
            
            if not documents:
                raise ValueError(f"Paper not found: {paper_id}")
            
            doc = documents[0]
            
            paper = {
                "id": f"arxiv:{paper_id}",
                "title": doc.metadata.get("Title", ""),
                "authors": doc.metadata.get("Authors", []),
                "published": doc.metadata.get("Published", ""),
                "summary": doc.metadata.get("Summary", ""),
                "full_text": doc.page_content,
                "pdf_url": doc.metadata.get("pdf_url", ""),
                "source": "arxiv",
                "metadata": doc.metadata
            }
            
            logger.info(f"Successfully loaded paper: {paper['title'][:50]}...")
            return paper
            
        except Exception as e:
            logger.error(f"Failed to load ArXiv paper {paper_id}: {e}")
            raise Exception(f"Failed to load paper: {str(e)}")
    
    def load_multiple(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Load multiple papers by their IDs.
        
        Args:
            paper_ids: List of ArXiv paper IDs
            
        Returns:
            List of paper dictionaries
        """
        papers = []
        for paper_id in paper_ids:
            try:
                paper = self.load_by_id(paper_id)
                papers.append(paper)
            except Exception as e:
                logger.warning(f"Skipping paper {paper_id}: {e}")
                continue
        
        logger.info(f"Loaded {len(papers)}/{len(paper_ids)} papers")
        return papers
    
    def to_langchain_documents(
        self,
        papers: List[Dict[str, Any]]
    ) -> List[Document]:
        """
        Convert paper dictionaries to LangChain Document objects.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for paper in papers:
            doc = Document(
                page_content=paper.get("full_text", paper.get("summary", "")),
                metadata={
                    "id": paper.get("id", ""),
                    "title": paper.get("title", ""),
                    "authors": ", ".join(paper.get("authors", [])),
                    "published": paper.get("published", ""),
                    "source": paper.get("source", "arxiv"),
                    "pdf_url": paper.get("pdf_url", ""),
                }
            )
            documents.append(doc)
        
        return documents