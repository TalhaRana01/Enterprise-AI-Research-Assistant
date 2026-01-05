"""Prompt template manager for loading and managing prompts."""

from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PromptManager:
    """
    Manages prompt templates for the research assistant.
    
    Loads prompts from text files and provides methods to retrieve them.
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt files (default: src/prompts/)
        """
        if prompts_dir is None:
            # Get prompts directory relative to this file
            current_file = Path(__file__)
            prompts_dir = current_file.parent
        
        self.prompts_dir = Path(prompts_dir)
        self._prompts: Dict[str, str] = {}
        
        logger.info(f"PromptManager initialized with directory: {self.prompts_dir}")
        self._load_all_prompts()
    
    def _load_all_prompts(self) -> None:
        """Load all prompt files from the prompts directory."""
        try:
            # Load all .txt files in prompts directory
            for prompt_file in self.prompts_dir.glob("*.txt"):
                prompt_name = prompt_file.stem  # filename without extension
                try:
                    with open(prompt_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        self._prompts[prompt_name] = content
                        logger.debug(f"Loaded prompt: {prompt_name}")
                except Exception as e:
                    logger.warning(f"Failed to load prompt {prompt_file}: {e}")
            
            logger.info(f"Loaded {len(self._prompts)} prompts")
            
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
    
    def get_prompt(self, name: str) -> str:
        """
        Get a prompt by name.
        
        Args:
            name: Prompt name (without .txt extension)
            
        Returns:
            Prompt content as string
            
        Raises:
            ValueError: If prompt not found
        """
        if name not in self._prompts:
            available = ", ".join(self._prompts.keys())
            raise ValueError(
                f"Prompt '{name}' not found. Available prompts: {available}"
            )
        
        return self._prompts[name]
    
    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.get_prompt("system_prompt")
    
    def get_search_prompt(self) -> str:
        """Get the search agent prompt."""
        return self.get_prompt("search_prompt")
    
    def get_qa_prompt(self) -> str:
        """Get the Q&A prompt template."""
        return self.get_prompt("qa_prompt")
    
    def get_summarization_prompt(self) -> str:
        """Get the summarization prompt template."""
        return self.get_prompt("summarization_prompt")
    
    def get_citation_prompt(self) -> str:
        """Get the citation prompt template."""
        return self.get_prompt("citation_prompt")
    
    def format_prompt(
        self,
        prompt_name: str,
        **kwargs
    ) -> str:
        """
        Format a prompt template with variables.
        
        Args:
            prompt_name: Name of the prompt template
            **kwargs: Variables to substitute in the prompt
            
        Returns:
            Formatted prompt string
            
        Example:
            prompt_manager.format_prompt(
                "qa_prompt",
                context="...",
                question="What is..."
            )
        """
        prompt = self.get_prompt(prompt_name)
        
        try:
            return prompt.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable in prompt {prompt_name}: {e}")
            raise ValueError(f"Missing required variable: {e}")
    
    def list_prompts(self) -> list[str]:
        """
        List all available prompt names.
        
        Returns:
            List of prompt names
        """
        return list(self._prompts.keys())
    
    def reload(self) -> None:
        """Reload all prompts from disk."""
        logger.info("Reloading prompts...")
        self._prompts.clear()
        self._load_all_prompts()


# Global prompt manager instance
_prompt_manager: Optional[PromptManager] = None


@lru_cache(maxsize=1)
def get_prompt_manager() -> PromptManager:
    """
    Get the global prompt manager instance (singleton).
    
    Returns:
        PromptManager instance
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def load_prompt(name: str) -> str:
    """
    Convenience function to load a prompt by name.
    
    Args:
        name: Prompt name
        
    Returns:
        Prompt content
    """
    return get_prompt_manager().get_prompt(name)

