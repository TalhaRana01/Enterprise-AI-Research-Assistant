"""Question-answering agent using RAG for research papers."""

from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger
from src.config import settings
from src.prompts import load_prompt
from src.chains import RAGChain, create_rag_chain
from src.tools import search_papers_tool

logger = get_logger(__name__)


class QAAgent:
    """
    Question-answering agent using RAG (Retrieval-Augmented Generation).
    
    Capabilities:
    - Answer questions about research papers
    - Search for relevant papers when needed
    - Use RAG to provide context-aware answers
    - Cite sources in responses
    """
    
    def __init__(
        self,
        rag_chain: Optional[RAGChain] = None,
        llm_model: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize Q&A agent.
        
        Args:
            rag_chain: RAG chain instance (default: creates new)
            llm_model: LLM model name (default: from settings)
            verbose: Enable verbose logging
        """
        self.llm_model = llm_model or settings.llm_model
        self.verbose = verbose
        
        logger.info(f"Initializing QAAgent: model={self.llm_model}")
        
        # Initialize RAG chain if not provided
        if rag_chain is None:
            self.rag_chain = create_rag_chain(llm_model=self.llm_model)
        else:
            self.rag_chain = rag_chain
        
        # Initialize LLM for agent reasoning
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key,
            request_timeout=settings.request_timeout
        )
        
        # Setup tools (search tool for finding papers)
        self.tools = [search_papers_tool]
        
        # Load Q&A prompt
        try:
            system_prompt = load_prompt("system_prompt")
        except Exception as e:
            logger.warning(f"Failed to load system_prompt, using default: {e}")
            system_prompt = """You are an expert AI Research Assistant designed to help researchers, 
students, and professionals find, analyze, and understand academic papers.

Your capabilities include:
- Answering questions about research papers using RAG
- Searching for relevant papers when needed
- Providing accurate, evidence-based answers
- Citing sources when referencing specific papers

Guidelines:
- Always provide accurate, evidence-based answers
- Cite sources when referencing specific papers
- Be clear and concise in explanations
- If you need to search for papers, use the search tool first
- Then use the RAG system to answer based on retrieved papers"""
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        # Simplified: Use RAG chain directly (no agent executor needed)
        logger.info("QAAgent initialized successfully (simplified mode)")
    
    def answer(
        self,
        question: str,
        paper_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question about research papers.
        
        Args:
            question: User's question
            paper_ids: Optional list of specific paper IDs to use
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            logger.info(f"QAAgent processing question: '{question[:50]}...'")
            
            # If specific papers provided, use RAG directly
            if paper_ids:
                # Load papers and add to vector store if needed
                # Then use RAG chain
                result = self.rag_chain.invoke(question)
                return {
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "question": question,
                    "method": "rag_direct"
                }
            
            # Otherwise, let agent decide (search first, then answer)
            # For now, use RAG chain directly (papers should be in vector store)
            result = self.rag_chain.invoke(question)
            
            logger.info("QAAgent completed successfully")
            return {
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "question": question,
                "num_sources": result.get("num_sources", 0),
                "method": "rag"
            }
            
        except Exception as e:
            logger.error(f"QAAgent failed: {e}")
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def answer_with_search(
        self,
        question: str,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer question after searching for relevant papers.
        
        Args:
            question: User's question
            search_query: Optional search query (if different from question)
            
        Returns:
            Answer with search results
        """
        try:
            # Use search query or question
            query = search_query or question
            
            logger.info(f"Answering with search: question='{question}', search='{query}'")
            
            # First search for papers (using search tool directly)
            from src.tools import search_papers_tool
            search_result = search_papers_tool.invoke({
                "query": query,
                "max_results": 10,
                "source": "arxiv"
            })
            
            # Then answer using RAG
            answer_result = self.rag_chain.invoke(question)
            
            return {
                "answer": answer_result.get("answer", ""),
                "sources": answer_result.get("sources", []),
                "search_results": search_result.get("output", ""),
                "question": question,
                "method": "search_then_rag"
            }
            
        except Exception as e:
            logger.error(f"Answer with search failed: {e}")
            raise Exception(f"Failed to answer with search: {str(e)}")
    
    def stream_answer(self, question: str):
        """
        Stream answer as it's generated.
        
        Args:
            question: User's question
            
        Yields:
            Answer chunks
        """
        try:
            logger.info(f"Streaming answer for: '{question[:50]}...'")
            
            for chunk in self.rag_chain.stream(question):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise Exception(f"Streaming failed: {str(e)}")


def create_qa_agent(
    rag_chain: Optional[RAGChain] = None,
    llm_model: Optional[str] = None,
    verbose: bool = False
) -> QAAgent:
    """
    Factory function to create a Q&A agent.
    
    Args:
        rag_chain: RAG chain instance
        llm_model: LLM model name
        verbose: Enable verbose logging
        
    Returns:
        QAAgent instance
    """
    return QAAgent(
        rag_chain=rag_chain,
        llm_model=llm_model,
        verbose=verbose
    )

