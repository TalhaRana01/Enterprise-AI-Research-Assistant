"""Summarization chain for creating summaries of research papers."""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger
from src.config import settings
from src.prompts import load_prompt

logger = get_logger(__name__)


class SummarizationChain:
    """
    Chain for summarizing research papers.
    
    Creates structured summaries with:
    - Overview
    - Key findings
    - Methodology
    - Contributions
    - Limitations
    - Conclusion
    """
    
    def __init__(self, llm_model: Optional[str] = None):
        """
        Initialize summarization chain.
        
        Args:
            llm_model: LLM model name (default: from settings)
        """
        self.llm_model = llm_model or settings.llm_model
        
        logger.info(f"Initializing SummarizationChain: model={self.llm_model}")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            openai_api_key=settings.openai_api_key
        )
        
        # Load summarization prompt template
        try:
            prompt_template = load_prompt("summarization_prompt")
        except Exception as e:
            logger.warning(f"Failed to load summarization_prompt, using default: {e}")
            prompt_template = """Create a detailed summary of the following research paper.

Title: {title}
Authors: {authors}
Published: {published}

Paper Content:
{content}

Create a comprehensive summary with:
1. Overview
2. Key Findings
3. Methodology
4. Contributions
5. Limitations
6. Conclusion

Summary:"""
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Build chain
        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("SummarizationChain initialized successfully")
    
    def summarize(
        self,
        title: str,
        content: str,
        authors: Optional[list[str]] = None,
        published: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize a research paper.
        
        Args:
            title: Paper title
            content: Paper content/text
            authors: List of authors (optional)
            published: Publication date (optional)
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            # Format authors
            authors_str = ", ".join(authors) if authors else "Unknown Authors"
            published_str = published or "Unknown Date"
            
            logger.info(f"Summarizing paper: {title[:50]}...")
            
            # Truncate content if too long (to avoid token limits)
            max_content_length = 8000  # Approximate token limit
            if len(content) > max_content_length:
                logger.warning(f"Content too long ({len(content)} chars), truncating...")
                content = content[:max_content_length] + "..."
            
            # Invoke chain
            summary = self.chain.invoke({
                "title": title,
                "authors": authors_str,
                "published": published_str,
                "content": content
            })
            
            result = {
                "summary": summary.strip(),
                "title": title,
                "authors": authors or [],
                "published": published_str,
                "length": len(summary)
            }
            
            logger.info(f"Generated summary ({len(summary)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise Exception(f"Failed to summarize paper: {str(e)}")
    
    def summarize_short(
        self,
        title: str,
        content: str,
        max_length: int = 200
    ) -> str:
        """
        Generate a short summary (abstract-like).
        
        Args:
            title: Paper title
            content: Paper content
            max_length: Maximum summary length
            
        Returns:
            Short summary string
        """
        try:
            logger.info(f"Generating short summary for: {title[:50]}...")
            
            # Use a simpler prompt for short summary
            short_prompt = ChatPromptTemplate.from_template(
                "Summarize the following research paper in {max_length} words or less.\n\n"
                "Title: {title}\n"
                "Content: {content}\n\n"
                "Summary:"
            )
            
            short_chain = short_prompt | self.llm | StrOutputParser()
            
            summary = short_chain.invoke({
                "title": title,
                "content": content[:4000],  # Limit content
                "max_length": max_length
            })
            
            logger.info(f"Generated short summary ({len(summary)} chars)")
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Short summarization failed: {e}")
            raise Exception(f"Failed to generate short summary: {str(e)}")
    
    def summarize_bullet_points(
        self,
        title: str,
        content: str,
        num_points: int = 5
    ) -> list[str]:
        """
        Generate summary as bullet points.
        
        Args:
            title: Paper title
            content: Paper content
            num_points: Number of bullet points
            
        Returns:
            List of bullet point strings
        """
        try:
            logger.info(f"Generating bullet points for: {title[:50]}...")
            
            bullet_prompt = ChatPromptTemplate.from_template(
                "Create {num_points} key bullet points summarizing this research paper.\n\n"
                "Title: {title}\n"
                "Content: {content}\n\n"
                "Bullet Points:\n"
            )
            
            bullet_chain = bullet_prompt | self.llm | StrOutputParser()
            
            result = bullet_chain.invoke({
                "title": title,
                "content": content[:4000],
                "num_points": num_points
            })
            
            # Parse bullet points
            points = [
                point.strip()
                for point in result.split("\n")
                if point.strip() and (point.strip().startswith("-") or point.strip().startswith("•"))
            ]
            
            # Clean up bullet markers
            points = [p.lstrip("- •").strip() for p in points]
            
            logger.info(f"Generated {len(points)} bullet points")
            return points[:num_points]  # Return requested number
            
        except Exception as e:
            logger.error(f"Bullet point summarization failed: {e}")
            raise Exception(f"Failed to generate bullet points: {str(e)}")


def create_summarization_chain(llm_model: Optional[str] = None) -> SummarizationChain:
    """
    Factory function to create a summarization chain.
    
    Args:
        llm_model: LLM model name
        
    Returns:
        SummarizationChain instance
    """
    return SummarizationChain(llm_model=llm_model)

