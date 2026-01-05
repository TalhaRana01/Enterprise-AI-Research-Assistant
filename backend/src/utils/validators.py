"""Input validation utilities."""

import re
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If input is invalid
    """
    if not text or not isinstance(text, str):
        raise ValueError("Input must be a non-empty string")
    
    # Trim whitespace
    text = text.strip()
    
    # Check length
    if len(text) > max_length:
        logger.warning(f"Input truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    return text


def validate_query(query: str) -> bool:
    """
    Validate search query.
    
    Args:
        query: Search query to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not query or len(query.strip()) < 3:
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onclick=",
        r"eval\(",
        r"exec\(",
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            logger.warning(f"Suspicious pattern detected in query: {pattern}")
            return False
    
    return True


def detect_prompt_injection(text: str) -> bool:
    """
    Detect potential prompt injection attempts.
    
    Args:
        text: Text to check
        
    Returns:
        True if injection detected, False otherwise
    """
    # Common prompt injection patterns
    injection_patterns = [
        r"ignore previous instructions",
        r"disregard all previous",
        r"forget everything",
        r"new instructions:",
        r"system:",
        r"admin mode",
        r"developer mode",
        r"jailbreak",
    ]
    
    text_lower = text.lower()
    
    for pattern in injection_patterns:
        if re.search(pattern, text_lower):
            logger.warning(f"Potential prompt injection detected: {pattern}")
            return True
    
    return False


def validate_paper_id(paper_id: str) -> bool:
    """
    Validate paper ID format.
    
    Args:
        paper_id: Paper ID to validate (e.g., "arxiv:2301.12345")
        
    Returns:
        True if valid, False otherwise
    """
    # ArXiv format: arxiv:YYMM.NNNNN
    arxiv_pattern = r"^arxiv:\d{4}\.\d{4,5}$"
    
    # PubMed format: pubmed:12345678
    pubmed_pattern = r"^pubmed:\d{8}$"
    
    # DOI format: doi:10.xxxx/xxxxx
    doi_pattern = r"^doi:10\.\d{4,}/[^\s]+$"
    
    patterns = [arxiv_pattern, pubmed_pattern, doi_pattern]
    
    for pattern in patterns:
        if re.match(pattern, paper_id, re.IGNORECASE):
            return True
    
    return False

