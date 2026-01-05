"""Citation generation chain for formatting research paper citations."""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger
from src.config import settings
from src.prompts import load_prompt

logger = get_logger(__name__)


class CitationChain:
    """
    Chain for generating citations in various formats.
    
    Supports:
    - APA style
    - MLA style
    - Chicago style
    - BibTeX format
    """
    
    def __init__(self, llm_model: Optional[str] = None):
        """
        Initialize citation chain.
        
        Args:
            llm_model: LLM model name (default: from settings)
        """
        self.llm_model = llm_model or settings.llm_model
        
        logger.info(f"Initializing CitationChain: model={self.llm_model}")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0,  # Low temperature for consistent formatting
            max_tokens=500,
            openai_api_key=settings.openai_api_key
        )
        
        # Load citation prompt template
        try:
            prompt_template = load_prompt("citation_prompt")
        except Exception as e:
            logger.warning(f"Failed to load citation_prompt, using default: {e}")
            prompt_template = """Generate a citation in {style} format for the following paper:

Title: {title}
Authors: {authors}
Year: {year}
Journal: {journal}
DOI: {doi}
URL: {url}

Citation ({style} format):"""
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Build chain
        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("CitationChain initialized successfully")
    
    def generate(
        self,
        title: str,
        authors: list[str],
        year: str,
        journal: Optional[str] = None,
        doi: Optional[str] = None,
        url: Optional[str] = None,
        style: str = "apa"
    ) -> str:
        """
        Generate citation in specified format.
        
        Args:
            title: Paper title
            authors: List of author names
            year: Publication year
            journal: Journal/conference name
            doi: DOI (optional)
            url: URL (optional)
            style: Citation style (apa, mla, chicago, bibtex)
            
        Returns:
            Formatted citation string
        """
        try:
            # Format authors
            authors_str = ", ".join(authors) if isinstance(authors, list) else authors
            
            logger.info(f"Generating {style} citation for: {title[:50]}...")
            
            # Invoke chain
            citation = self.chain.invoke({
                "title": title,
                "authors": authors_str,
                "year": year or "n.d.",
                "journal": journal or "",
                "doi": doi or "",
                "url": url or "",
                "style": style.lower()
            })
            
            logger.info(f"Generated {style} citation successfully")
            return citation.strip()
            
        except Exception as e:
            logger.error(f"Citation generation failed: {e}")
            raise Exception(f"Failed to generate citation: {str(e)}")
    
    def generate_apa(
        self,
        title: str,
        authors: list[str],
        year: str,
        journal: Optional[str] = None,
        doi: Optional[str] = None
    ) -> str:
        """Generate APA format citation."""
        return self.generate(
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            doi=doi,
            style="apa"
        )
    
    def generate_mla(
        self,
        title: str,
        authors: list[str],
        year: str,
        journal: Optional[str] = None
    ) -> str:
        """Generate MLA format citation."""
        return self.generate(
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            style="mla"
        )
    
    def generate_chicago(
        self,
        title: str,
        authors: list[str],
        year: str,
        journal: Optional[str] = None
    ) -> str:
        """Generate Chicago format citation."""
        return self.generate(
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            style="chicago"
        )
    
    def generate_bibtex(
        self,
        title: str,
        authors: list[str],
        year: str,
        journal: Optional[str] = None,
        paper_id: Optional[str] = None
    ) -> str:
        """Generate BibTeX format citation."""
        return self.generate(
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            style="bibtex"
        )
    
    def generate_all_formats(
        self,
        title: str,
        authors: list[str],
        year: str,
        journal: Optional[str] = None,
        doi: Optional[str] = None,
        url: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate citations in all formats.
        
        Returns:
            Dictionary with all citation formats
        """
        try:
            logger.info(f"Generating all citation formats for: {title[:50]}...")
            
            citations = {
                "apa": self.generate_apa(title, authors, year, journal, doi),
                "mla": self.generate_mla(title, authors, year, journal),
                "chicago": self.generate_chicago(title, authors, year, journal),
                "bibtex": self.generate_bibtex(title, authors, year, journal)
            }
            
            logger.info("Generated all citation formats successfully")
            return citations
            
        except Exception as e:
            logger.error(f"Failed to generate all formats: {e}")
            raise Exception(f"Citation generation failed: {str(e)}")


def create_citation_chain(llm_model: Optional[str] = None) -> CitationChain:
    """
    Factory function to create a citation chain.
    
    Args:
        llm_model: LLM model name
        
    Returns:
        CitationChain instance
    """
    return CitationChain(llm_model=llm_model)

