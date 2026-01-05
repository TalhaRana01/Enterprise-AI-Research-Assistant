"""Output formatting utilities."""

from typing import List, Dict, Any
from datetime import datetime


def format_paper_summary(paper: Dict[str, Any]) -> str:
    """
    Format paper information for display.
    
    Args:
        paper: Paper metadata dictionary
        
    Returns:
        Formatted paper summary
    """
    title = paper.get("title", "Unknown Title")
    authors = paper.get("authors", [])
    year = paper.get("year", "Unknown")
    abstract = paper.get("abstract", "No abstract available")
    
    authors_str = ", ".join(authors[:3])
    if len(authors) > 3:
        authors_str += f" et al. ({len(authors)} authors)"
    
    return f"""
Title: {title}
Authors: {authors_str}
Year: {year}

Abstract:
{abstract[:500]}{'...' if len(abstract) > 500 else ''}
    """.strip()


def format_citation(paper: Dict[str, Any], style: str = "apa") -> str:
    """
    Format paper citation in specified style.
    
    Args:
        paper: Paper metadata dictionary
        style: Citation style (apa, mla, chicago, bibtex)
        
    Returns:
        Formatted citation
    """
    if style == "apa":
        return format_apa_citation(paper)
    elif style == "mla":
        return format_mla_citation(paper)
    elif style == "chicago":
        return format_chicago_citation(paper)
    elif style == "bibtex":
        return format_bibtex_citation(paper)
    else:
        return format_apa_citation(paper)


def format_apa_citation(paper: Dict[str, Any]) -> str:
    """Format citation in APA style."""
    authors = paper.get("authors", [])
    year = paper.get("year", "n.d.")
    title = paper.get("title", "Unknown title")
    journal = paper.get("journal", "")
    doi = paper.get("doi", "")
    
    # Format authors (Last, F. M.)
    author_str = ""
    for i, author in enumerate(authors[:7]):
        if i > 0:
            author_str += ", "
        if i == 6 and len(authors) > 7:
            author_str += "... "
        parts = author.split()
        if parts:
            last_name = parts[-1]
            initials = " ".join([p[0] + "." for p in parts[:-1]])
            author_str += f"{last_name}, {initials}"
    
    citation = f"{author_str} ({year}). {title}."
    
    if journal:
        citation += f" {journal}."
    
    if doi:
        citation += f" https://doi.org/{doi}"
    
    return citation


def format_mla_citation(paper: Dict[str, Any]) -> str:
    """Format citation in MLA style."""
    authors = paper.get("authors", [])
    title = paper.get("title", "Unknown title")
    journal = paper.get("journal", "")
    year = paper.get("year", "n.d.")
    
    if authors:
        first_author = authors[0]
        parts = first_author.split()
        if parts:
            author_str = f"{parts[-1]}, {' '.join(parts[:-1])}"
            if len(authors) > 1:
                author_str += ", et al"
    else:
        author_str = "Unknown Author"
    
    citation = f'{author_str}. "{title}."'
    
    if journal:
        citation += f" {journal},"
    
    citation += f" {year}."
    
    return citation


def format_chicago_citation(paper: Dict[str, Any]) -> str:
    """Format citation in Chicago style."""
    authors = paper.get("authors", [])
    year = paper.get("year", "n.d.")
    title = paper.get("title", "Unknown title")
    journal = paper.get("journal", "")
    
    if authors:
        first_author = authors[0]
        parts = first_author.split()
        if parts:
            author_str = f"{parts[-1]}, {' '.join(parts[:-1])}"
            if len(authors) > 1:
                author_str += ", and " + ", ".join(authors[1:3])
                if len(authors) > 3:
                    author_str += ", et al"
    else:
        author_str = "Unknown Author"
    
    citation = f'{author_str}. {year}. "{title}."'
    
    if journal:
        citation += f" {journal}."
    
    return citation


def format_bibtex_citation(paper: Dict[str, Any]) -> str:
    """Format citation in BibTeX style."""
    paper_id = paper.get("id", "unknown")
    authors = " and ".join(paper.get("authors", ["Unknown"]))
    title = paper.get("title", "Unknown title")
    year = paper.get("year", "")
    journal = paper.get("journal", "")
    
    bibtex = f"""@article{{{paper_id},
    author = {{{authors}}},
    title = {{{title}}},
    year = {{{year}}},"""
    
    if journal:
        bibtex += f"\n    journal = {{{journal}}},"
    
    bibtex += "\n}"
    
    return bibtex


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results for display.
    
    Args:
        results: List of search result dictionaries
        
    Returns:
        Formatted results string
    """
    if not results:
        return "No results found."
    
    output = f"Found {len(results)} results:\n\n"
    
    for i, result in enumerate(results, 1):
        title = result.get("title", "Unknown")
        authors = result.get("authors", [])
        year = result.get("year", "")
        score = result.get("score", 0.0)
        
        authors_str = ", ".join(authors[:2])
        if len(authors) > 2:
            authors_str += " et al."
        
        output += f"{i}. {title}\n"
        output += f"   Authors: {authors_str}\n"
        output += f"   Year: {year} | Relevance: {score:.2f}\n\n"
    
    return output

